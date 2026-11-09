import os
import subprocess # Launches and manages external programs from inside Python
import matplotlib.pyplot as plt

airfoils = ['n0009sm.dat', 'n0012.dat', 'naca2412.dat', 'naca4412.dat']
results = {}

for airfoil in airfoils:
    polar_filename = f"polar_{airfoil.split('.')[0]}.txt"
    if os.path.exists(polar_filename): # checks if the file exsists in the harddrive
        os.remove(polar_filename)# delets it Permanently from the disc

    command = f'''
    PLOP
    G

    LOAD {airfoil}
    PANE 
    OPER
    Visc 1000000
    PACC
    {polar_filename}

    ASEQ 0 10 2

    QUIT
    '''

    # PANE - repanneling(smoothing the nodes points along the airfoil surface)
    # OPER = Enters the main operational menus while making aerodynamic calculation
    # Visc = sets the reynolds number (the re = 1000000 represnts the reynolds number for normal sized aircraft or drones)
    # re = VL/dynamic velocity, dynamic velocity = viscosity/density(eg. Boeing 737(re = 30mil))
    #PLOP /nG = disables xfoils PltLib graphics window

    with open('cmd.txt', 'w') as f:
        f.write(command.strip()) 
    
    with open('cmd.txt', 'r') as cmd_file:
        # The clean, standard way to run XFOIL silently:
        subprocess.run(['xfoil'], stdin=cmd_file, stdout=subprocess.DEVNULL)
                                                  # prevents the text printed while Xfoil runs from becoming visible
    if os.path.exists(polar_filename):
        cl_values = []
        alpha_values = []

        with open(polar_filename, 'r') as pf:                                              
            lines = pf.readlines() # whats in polar_filename is read as a list of stings. (eg, ["\n", "XFOIL Version 6.99\n", ..., " 0.000  0.0001 ...\n"])
            for line in lines:
                parts = line.strip().split() # removes white spaces and divides the line by white spaces (eg, ' 0.000   0.0001   0.00422' ->  ['0.000', '0.0001', '0.00422', ...])
                if len(parts) > 1 and parts[0].replace('.', '', 1).isdigit(): # '2.000'-> '2000'
                    alpha_values.append(float(parts[0])) 
                    cl_values.append(float(parts[1]))  

        if cl_values:
            max_cl = max(cl_values)
            max_alpha = alpha_values[cl_values.index(max_cl)]
            results[airfoil] = {'max_cl': max_cl, 'alpha': max_alpha, 'alpha_seq': alpha_values, 'cl_seq': cl_values}

print("\n--- Optimization Results ---")
Best_airfoil = max(results, key = lambda x: results[x]['max_cl'])
for af, data in results.items():
    print(f"Airfoil: {af} | Max Cl: {data['max_cl']:.3f} at Alpha: {data['alpha']}°")     
    
print(f"\n[BEST] Best performing airfoil for max lift: {Best_airfoil}")

plt.figure(figsize=(8, 5))
for af, data in results.items():
    plt.plot(data['alpha_seq'], data['cl_seq'], marker='o', label=af)

plt.title('Lift Coefficient (Cl) vs Angle of Attack (Alpha)')
plt.xlabel('Angle of Attack (deg)')
plt.ylabel('Lift Coefficient (Cl)')
plt.grid(True)
plt.legend()
plt.savefig('airfoil_optimization_results.png')
plt.show()