# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 11:20:10 2024

@author: hah
"""
from sympy import symbols, Eq, solve
import math
from scipy.optimize import fsolve

def Calculation(H_R,B,Fck,H_slab,M,V,N,H):
    ### Given ###
    Gamma_c = 1.5  # Safety factor for concrete (GIVEN)
    Gamma_s = 1.15 # Safety factor for steel (GIVEN)
    Gamma_s_prime = 1.04 # Safety factor for steel (GIVEN)
    Gamma_v_prime = 1.29 # Safety factor for steel (GIVEN)
    Gamma_v = 1.4 # Safety factor for steel (GIVEN)
    Gamma_M0 = 1.00
    
    Fsk=500 # Mpa : Steel resistance of the slab reinforcement(GIVEN)
    Fsk_prime = 550 #Mpa : Steel resistance for the area of steel welded to the profile (GIVEN)
    Es_prime = 210 *10**3 # Mpa (Elastic Modulus) 
    Fyk = 450 # Mpa (For Profile)
    
    d_g = 32 #mm Aggregate diameter (GIVEN)
    Cc = 30  #Concrete cover (GIVEN)
    
    A_s = 157 #mm2 (Area of steel welded to the profile) (Given)
    x = 55 #mm (Given - to confirm)
    m_del = 25 * 10**6 # Mpa (Given - to confirm)
    K_c = 2
    A_c = 1000
    b = 50 # mm
    Alfa = 30 # degree
    R_welds = 110 *10**3 #N (Given)
    w = 3 # mm (width of web profile)
    phi = 12 #mm Diameter of slab reinforcement
    
    if M == 0:
        M = 1e-10
    if V == 0:
        V = 1e-10
    if N == 0:
        N = 1e-10        
    if H == 0:
        H = 1e-10 
            
    if M < 0 :
        M = abs(M)     
    if V < 0 :
        V = abs(V)    
    if N < 0 :
        N = abs(N)
               
    z_slab = (H_slab - 2*Cc - 16) #mm (GIVEN)
        
    if H_R ==11:
        z   = 94          #mm
        V_pl= 83.4 *1000  #kN
        M_pl= 7.4  *10**6 #kNm
    
    if H_R ==13:
        z   = 114         #mm
        V_pl= 99.0 *1000  #kN
        M_pl= 9.7  *10**6 #kNm
    
    if H_R ==15:
        z   = 134         #mm
        V_pl= 114.5 *1000  #kN
        M_pl= 12.2 *10**6 #kNm
    
    if H_R ==17:
        z   = 154          #mm
        V_pl= 130.1 *1000  #kN
        M_pl= 15.0  *10**6 #kNm
            
    if H_R ==19:
        z   = 174          #mm
        V_pl= 145.7 *1000  #kN
        M_pl= 18.1  *10**6 #kNm
    
    if z_slab < z:
        z_slab = z
        Gamma_v = Gamma_v_prime 
        
        
    ##### SOLVE [EQUATION 1] FOR N(NUMBER OF RIBS) #####
    n1 = (M+V*x)/(A_s*Fsk_prime*z*(1/Gamma_s_prime))
    
    ##### SOLVE [EQUATION 2] FOR N(NUMBER OF RIBS) #####
    if M > (m_del -x*V):    
        # Define the function representing the equation
        def equation(n):
            term1 = 1000 * z * math.sqrt(Fck) * 0.3 / Gamma_v_prime
            term2 = (50 / (16 + d_g)) * (Fsk_prime / (Gamma_s_prime * Es_prime))
            term3 = z * ((M) + V * x) / (n * A_s * Fsk_prime * z / Gamma_s_prime)
            return V - (term1 / (1 + term2 * term3))    
        # Initial guess for n
        n_initial_guess = 0.1
        
        # Use fsolve to find the root of the equation
        n_solution = fsolve(equation, n_initial_guess)        
        n2 = n_solution[0]        
    
    elif M<= (m_del -x*V):
        # Define the function representing the equation
        def equation(n):
            term1 = 1000 * z_slab * math.sqrt(Fck) * 0.3 / Gamma_v
            term2 = (50 / (16 + d_g)) * (Fsk_prime / (Gamma_s_prime * Es_prime))
            term3 = z_slab * ((M) + V * x) / (n * A_s * Fsk_prime * z / Gamma_s_prime)
            return V - (term1 / (1 + term2 * term3))
        
        # Initial guess for n
        n_initial_guess = 0.1
        
        # Use fsolve to find the root of the equation
        n_solution = fsolve(equation, n_initial_guess)        
        n2 = n_solution[0]
    
    ##### SOLVE [EQUATION 3 Updated] FOR N(NUMBER OF RIBS) #####  
    n3= V / (K_c*A_c *(Fck/Gamma_c)) 
    
    ##### SOLVE [EQUATION 4 and 5] FOR N(NUMBER OF RIBS) ##### 
    S = 200 #mm : Spacing of stirrups
    Asw = (V * S * Gamma_s) / Fsk
    n5 = (V*Gamma_s)/(Asw*2*Fsk)
    
    ##### SOLVE [EQUATION 6] FOR N(NUMBER OF RIBS) #####   
    n6 = 0.1
    for i in range(1,101):    
        if R_welds <= math.sqrt(((V/n6)**2.0) + ((M+V*x)/(z*n6))**2.0) :
            n6 = n6+0.1
            if R_welds >= math.sqrt(((V/n6)**2.0) + ((M+V*x)/(z*n6))**2.0):
                break
    
    #### SOLVE [EQUATION 7] FOR N(NUMBER OF RIBS) ##### 
    n7 = n1
    
    if  V < (V_pl*n7/2):
        n7 = (M+(x-25)*V)/M_pl
    
    elif (V_pl*n7/2)/10**3 < V/10**3 < (V_pl*n7)/10**3:
        n7 = symbols('n7')
        expr = Eq(M_pl * n7 -((((2*V)/(n7*V_pl)-1))**2)*(Fyk/Gamma_M0)*((z/2)**2)*w*n7-(x-25)*V - M,0)
        n7_solutions = solve(expr, n7)
        n7 = max(n7_solutions)
    
    n1 = round(n1, 3)
    n2 = round(n2, 3)
    n3 = round(n3, 3)
    n5 = round(n5, 3)
    n6 = round(n6, 3)
    n7 = round(n7, 3)
    
    A_max = max(n1,n2,n3,n5,n6,n7)     
    
    ### Calculate Axial Capacity: 
    Nrd = 150 # For 1 rib    
    n_axial = N/Nrd     
    n_Total =  A_max + n_axial
    n = math.ceil(n_Total)    
        
    ######## Lateral resistance ##################################################################################
    # Define the main equation (10)
    t_insulation = int(B) * 10
    f_profile = 25  # Flange in mm
        
    # Define your coefficients 
    a_eq10 = z * math.sqrt(3) / t_insulation - 1
    b_eq10 = -(z + 2 * math.sqrt(3) * z * f_profile / t_insulation + math.sqrt(3) * V / (w * Fyk*n))
    c_eq10 = z * f_profile + z**2 / 4 - 3 * V**2 / (4 * w**2 * Fyk**2 * n**2) - (M + V * (x - 55)) / (w * Fyk*n)
        
    # Calculate the discriminant
    discriminant = b_eq10**2 - 4 * a_eq10 * c_eq10
                                        
    if discriminant >= 0: 
        # Calculate two possible solutions for p
        p1 = (-b_eq10 + math.sqrt(discriminant)) / (2 * a_eq10)
        p2 = (-b_eq10 - math.sqrt(discriminant)) / (2 * a_eq10)
    else:
        # Handle case where discriminant is negative (no real solutions)
        p1 = 0
        p2 = 0  
            
    # Ensure p1 and p2 are non-negative
    p1 = max(p1,0)
    p2 = max(p2,0)
    p =  min(p1,p2)
        
    # Coefficients for condition equation 
    a_con = math.sqrt(3) / t_insulation
    b_con = -(1 + 2 * math.sqrt(3) * f_profile / t_insulation)
    c_con = f_profile
       
    # Calculate the discriminant of the condition equation
    discriminant_cond = b_con**2 - 4*a_con*c_con
        
    # Calculate the two solutions
    root1 = (-b_con + math.sqrt(discriminant_cond)) / (2*a_con)
    root2 = (-b_con - math.sqrt(discriminant_cond)) / (2*a_con)
    # Get the lower value of p
    p_con = min(root1, root2)
        
    # Update p if p is less than p_con
    if p > p_con:
        p = p_con
        
    # Define m_h_Rd eq(12)
    m_h_Rd = (n * p * w * Fyk * (f_profile - p / 2))/1000000
        
    # Define v_h_Rd eq(13)
    v_h_Rd = (2 * m_h_Rd*1000000 / t_insulation)/1000
        
    # Collect number of ribs needed for resisting vertical loads to assign the range of the for loop
    n_vertical_loads_n_Total = n_Total
    n_vertical_loads = n
    v_h_Rd_Verical_loads = round(v_h_Rd,2)
    
    ########################################################################### 
    # Set intial condition as False so horizontal forces dont exist
    Presence_Horz_Load = False
    if H > 0.01: # 0.01 and not zero because we set H=1e-10
        Presence_Horz_Load = True
        
    for ribs in range(n_vertical_loads, 11):  
        if H > v_h_Rd+0.01: ## 0.01 is because when H is zero, actually it is 1e-10 for not having zeros/errors  
            n += 1 
            # Define your coefficients 
            a_eq10 = z * math.sqrt(3) / t_insulation - 1
            b_eq10 = -(z + 2 * math.sqrt(3) * z * f_profile / t_insulation + math.sqrt(3) * V / (w * Fyk*n))
            c_eq10 = z * f_profile + z**2 / 4 - 3 * V**2 / (4 * w**2 * Fyk**2 * n**2) - (M + V * (x - 55)) / (w * Fyk*n)
            # Calculate the discriminant
            discriminant = b_eq10**2 - 4 * a_eq10 * c_eq10                           
            if discriminant >= 0: 
                # Calculate two possible solutions for px
                p1 = (-b_eq10 + math.sqrt(discriminant)) / (2 * a_eq10)
                p2 = (-b_eq10 - math.sqrt(discriminant)) / (2 * a_eq10)
            else:
                # Handle case where discriminant is negative (no real solutions)
                p1 = 0
                p2 = 0     
            # Ensure p1 and p2 are non-negative
            p1 = max(p1, 0)
            p2 = max(p2, 0)
            p = min(p1,p2)
            # Coefficients for condition equation 
            a_con = math.sqrt(3) / t_insulation
            b_con = -(1 + 2 * math.sqrt(3) * f_profile / t_insulation)
            c_con = f_profile
            # Calculate the discriminant
            discriminant_cond = b_con**2 - 4*a_con*c_con
            # Calculate the two solutions
            root1 = (-b_con + math.sqrt(discriminant_cond)) / (2*a_con)
            root2 = (-b_con - math.sqrt(discriminant_cond)) / (2*a_con)
            # Get the lower value of p
            p_con = min(root1, root2)
            # Update p if p is less than p_con
            if p > p_con:
                p = p_con
                
            # Define m_h_Rd (12)
            m_h_Rd = (n * p * w * Fyk * (f_profile - p / 2))/1000000
            # Define v_h_Rd (13)
            v_h_Rd = (2 * m_h_Rd*1000000 / t_insulation)/1000
    
        else:
            break
    n_vert_and_Horz_loads = n    
    
    return n_vertical_loads_n_Total , n_vertical_loads , v_h_Rd_Verical_loads , n_vert_and_Horz_loads , v_h_Rd, Presence_Horz_Load
    
    
    
    
    
    