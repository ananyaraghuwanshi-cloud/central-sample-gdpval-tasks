#################################################################################
###                          Date: April 1st 2026                             ###
### This code first calibrates experimental uniaxial creep testing data       ###
### using a time-hardening power-law creep model from the excel file          ###
### Testing_Results.xlsx.  These calibrated coefficients are then used to     ###
### predict the relaxation of stress in a linkage using the strain-hardening  ###
### form to correctly account for changing stress.                            ###
#################################################################################




import numpy as np
import pandas as pd
from scipy.optimize import least_squares
import matplotlib.pyplot as plt


#Modifiable Inputs
diameter = 2.0 #mm
preload = 20.0 #N
leverRatio = 1.0/3.0


#Fixed Variables
gaugeArea = 13.0 * 3.2 #mm^2 - from ASTM D638 Type I
seconds_per_day = 86400.0


youngsModulus = 940.15 #MPA  - taken from inital loadup slope (first 2s)


#Extract material testing data
df = pd.read_excel("Testing_Results.xlsx", sheet_name="23C", header=None)
start_idx = 2


#First stress level test
test1_time = df.iloc[start_idx:,0].astype(np.float64).values
test1_force = df.iloc[start_idx:,1].astype(np.float64).values
test1_strain = df.iloc[start_idx:,2].astype(np.float64).values
test1_stress = test1_force / gaugeArea


#Second stress level test
test2_time = df.iloc[start_idx:,5].astype(np.float64).values
test2_force = df.iloc[start_idx:,6].astype(np.float64).values
test2_strain = df.iloc[start_idx:,7].astype(np.float64).values
test2_stress = test2_force / gaugeArea


#Combine for later regression
allTest_time = np.concatenate((test1_time,test2_time))
allTest_strain = np.concatenate((test1_strain,test2_strain))
allTest_stress = np.concatenate((test1_stress,test2_stress))


#######################################################
### Calibrate model using time hardeining power-law ###
#######################################################


#Calculate the difference between the expiremental and simulated strain
def residual(params, t, expStress, expStrain, E):
    A, n, m = params


    #use the intefrated from of time-harding to get total creep strain
    if np.abs(m+1) < 1e-12:  #Avoid case where m+1 approaches zero
        creepStrain = A * (expStress**n) * np.log(t + 1e-10)
    else:
        creepStrain = A * (expStress**n) * (t**(m+1)) / (m+1)


    predTotalStrain = expStress/E + creepStrain
    return  expStrain - predTotalStrain    




#Now use a least-squares reggression to fit the model parameters
p0 = [1e-8, 1.0, -.3]  #initial guess
bounds = ([1e-15,.5,-1.0],[0.001,25,0])
res = least_squares(residual, p0, args = (allTest_time, allTest_stress, allTest_strain, youngsModulus), bounds=bounds)
A_fit, n_fit, m_fit = res.x








print(f"A: {A_fit:3e}")
#A_fit = 1.410e-06 s^-(m+1) / MPA^n
print(f"n: {n_fit:3f}")
#n_fit = 0.986
print(f"m: {m_fit:3f}")
#m_fit = -0.719


########################################
### Solve for Linkage Stress vs Time ###
########################################


#Calculate initial state of linkage
initialLinkageForce = preload / leverRatio
linkageArea = np.pi * (diameter/2.0)**2
initialLinkageStress = initialLinkageForce / linkageArea
initialLinkageStrain = initialLinkageStress / youngsModulus


#Early high creep rate phase
dt_fine = 0.001 #seconds
n_fine = 3600.0 /dt_fine
t_fine = np.arange(n_fine) * dt_fine


#Later lower creep rate phase
dt_coarse = 500.0 #seconds
t_end = 3.0 *  365.0 * seconds_per_day
t_coarse = np.arange(t_fine[-1] + dt_coarse, t_end + dt_coarse/2,dt_coarse, dtype= np.float64)


#Combine stages
t_sim = np.concatenate((t_fine,t_coarse))
stress_sim = np.zeros_like(t_sim,dtype=np.float64)
stress_sim[0] = initialLinkageStress


#Seed initial, small non-zero creep strain to avoid numerical instability
creepStrain = 1e-6


#march through time calcualting accumulated creep 
for i in range(1, len(t_sim)):
    dt = t_sim[i] - t_sim[i-1]
    curStress = stress_sim[i-1]


    #Use STRAIN hardening form here - avoid numerical issues as creepstrain or (m+1) approach 0
    if creepStrain > 1e-20 and np.abs(m_fit +1) > 1e-20:
        inner_term = (A_fit * curStress**n_fit) * ((m_fit +1)*creepStrain)**m_fit
        if inner_term> 0.0:
            exponent = 1.0/ (m_fit + 1.0)
            creepRate = inner_term**exponent
        else:
            creepRate = 0.0
    else:
        #Set to 0 if creep strain is very small for stability
        creepRate = 0.0


    deltaCreepStrain = creepRate * dt
    creepStrain = creepStrain + deltaCreepStrain
    deltaStress = -youngsModulus * deltaCreepStrain
    stress_sim[i] = max(0,curStress + deltaStress)     #Avoid negitive case


t_days = t_sim /seconds_per_day


#Grab final results
finalStress = stress_sim[-1]
finalCreepStrain = initialLinkageStrain - finalStress/youngsModulus
creepPercent = finalCreepStrain * 100.0


print(f"Final stress: {finalStress:.3f}")
print(f"Final Creep Strain: {creepPercent:.2f}%")
#Final Creep Strain = 0.97%


#Warning Message if creep strain > 5%
if finalCreepStrain > 0.05:
    print(f"Warning: Creep strain exceeds 5% - Creep strain = {creepPercent: .2f}")


#Plot relaxation curve
plt.figure(figsize=(10,6))
plt.plot(t_days, stress_sim,'b-', linewidth = 2)
plt.xlabel("Time (days)", fontweight= 'bold')
plt.ylabel("Engineering Stress (MPa)", weight= 'bold')
plt.title(f"Linkage Stress vs Time (April 1, 2026)\n Fitted Material Parameters: E={youngsModulus:.3f} MPa, A={A_fit:.3e} s^-(m+1)/MPa^n, n={n_fit:.3f}, m={m_fit:.3f}", weight= 'bold')
plt.grid(True)
plt.ylim(0)


#Add final stress and creep strain to plot
plt.text(t_days[-1]*.8, finalStress*1.2,f'Final Stress:{finalStress: .2f} MPa \nFinal Creep Strain: {creepPercent:.2f}%',fontsize= 12, bbox=dict(facecolor='white',alpha=0.8))
plt.tight_layout()
plt.show()