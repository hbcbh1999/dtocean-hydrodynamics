#!/usr/bin/python2.7
# encoding: utf-8
"""
This module provides several tools which are recurrently used in water-wave problems

.. module:: input
   :platform: Windows
   :synopsis: Input module to DTOcean WP2

.. moduleauthor:: Pau Mercadez Ruiz <pmr@civil.aau.dk>
"""

# Start logging
import logging
module_logger = logging.getLogger(__name__)

from math import tanh, tan, cos, pi, log10
from numpy import array, zeros, ones, meshgrid, where, sqrt, arctan2, real, exp, cosh,\
NaN, float64, int32, ceil, conj
from scipy.special import jv, yv
import subprocess
import os

ro = 1000
g = 9.81

def Dispersion_T(L, const):
    """
    Linear dispersion equation, f=0, for travelling modes
    """

    T,h= const
    A= g*T**2/2/pi
    B= 2*pi*h
    f= L-A*tanh(B/L)
    df= 1-(A*B*(tanh(B/L)**2-1))/L**2
    return f,df

def Dispersion_E(L, const):
    """
    Linear dispersion equation, f=0, for evanescent modes
    """
    T,h= const
    A= g*T**2/2/pi
    B= 2*pi*h
    f= L+A*tan(B/L)
    df= 1-A*B/cos(B/L)**2/L**2 
    return f,df
    
def Newton(func, const, x= 1, feat= (100,1e-6,1e-6)):
    """
    Newton method for solving zeros of non-linear equations
    Args:
        func=f(x)=0 is the non-linear equation
        const is a tuple consisting of the f constants
        x is the first iterate
        feat is a tuple consisting of the max. number of iterates, the tolerance in x and f
    """
    kmax,Tol_x,Tol_f= feat
    found= 0
    k= 0
    while found == 0 and k < kmax:
        k+= 1 # Update k
        " Evaluating f and df "
        f,df= func(x,const)
        " Avoiding dividing by zero "
        if abs(df) < Tol_f*1e-3:
            found= 1
            bl= (0,'Local minimum. log|f| = {:.2f}'.format(log10(abs(f)+1e-99)))
        else:
            " Update x "
            x0= x
            x+= -f/df
            " Check on convergence "
            if abs(x-x0) < Tol_x and abs(f) < Tol_f:
                found= 1
                bl= (1,'Converged in {} iterations and with log|f| = {:.2f}'.format(k,log10(abs(f)+1e-99)))
    " Did not converge "
    if found == 0:
        bl= (0,'Did not converge. log|f| = {:.2f}'.format(log10(abs(f)+1e-99)))
    return x,bl
    
def WNumber(period, depth):
    """
    Calculates wave-number, k0, from wave-period and water depth (T,h).
        Dispersion relationship for travelling modes

    Args:
        period: a float or a list of float numbers. Wave periods
        depth: float(). It is the water depth.
    Outputs:
        wavenumbers
    """
    try :
        L = array([Newton(Dispersion_T, (p, depth))[0] for p in period], dtype=float)
    except TypeError:
        L = Newton(Dispersion_T, (period, depth))[0]
    return 2*pi/L

def len2(x):
    """
    len2 is used to get the len even if the object does not have the method
    """
    try:
        if type(x) == int or type(x) == float or \
        type(x) == int32 or type(x) == float64: return 1
        else : return len(x)
    except TypeError:
        raise TypeError('Attempted len2(x) but type(x) = {} is not supported in this version'.format(type(x)))
    
def WriteVariableinFile(variable, filename):
    """
    unused TBD
    """
    F= open(filename, 'w')
    ax= variable.shape
    if len2(ax) == 1:
        s= str(variable)[1:-1]
        F.write(s)
    elif len2(ax) == 2:
        for i in range(ax[0]):
            s= [format(variable[i,ii],'e') for ii in range(ax[1])]
            s= ' '.join(s)
            line= ''.join((s,'\n'))
            F.write(line)
    elif len2(ax) == 3:
        for i in range(ax[0]):
            for ii in range(ax[1]):
                s= [format(variable[i,ii,iii],'e') for iii in range(ax[2])]
                s= ' '.join(s)
                line= ''.join((str(i),' ',s,'\n'))
                F.write(line)
    elif len2(ax) == 4:
        for i in range(ax[0]):
            for ii in range(ax[1]):
                for iii in range(ax[2]):
                    s= [format(variable[i,ii,iii,iv],'e') for iv in range(ax[3])]
                    s= ' '.join(s)
                    line= ''.join((str(i),' ',str(ii),' ',s,'\n'))
                    F.write(line)
    F.close()
    
def CylWaveField(X, Y, Z, amplitudes, freq, wnumber, wdepth, Bodiescoord, disregard, plane=0):
    """
    unused TBD
    """
    NumBodies= len2(Bodiescoord)
    Nm= (len2(amplitudes)/NumBodies-1)/2
    mode= range(-Nm,Nm+1)
    XX, YY= meshgrid(X, Y, indexing='ij', sparse=True)
    Phii= zeros((NumBodies,XX.shape[0],YY.shape[1]), dtype=complex)
    for i in range(NumBodies):
        Xi, Yi= Bodiescoord[i]
        ri= sqrt((XX-Xi)**2+(YY-Yi)**2)
        thetai= arctan2(YY-Yi,XX-Xi)
        Phii[i][ri<=disregard]= NaN
        a= amplitudes[(2*Nm+1)*i:(2*Nm+1)*(i+1)]
        for m in mode[Nm:]:
            Psii= jv(m,wnumber*ri)-1j*yv(m,wnumber*ri)
            if plane == 1:
                Phii[i]+= a[Nm+m]*real(Psii)*exp(1j*m*thetai)
                if m>0:
                    Phii[i]+= a[Nm-m]*real((-1)**m*Psii)*exp(1j*-m*thetai)
            else :
                Phii[i]+= a[Nm+m]*Psii*exp(1j*m*thetai)
                if m>0:
                    Phii[i]+= a[Nm-m]*(-1)**m*Psii*exp(1j*-m*thetai)
    Phii*= 1j*g/freq
    if len2(Z) == 1:
        return cosh(wnumber*(Z+wdepth))/cosh(wnumber*wdepth)*Phii
    else :
        "Velocity potential"
        return array([cosh(wnumber*(z+wdepth))/cosh(wnumber*wdepth)*Phii for z in Z], dtype=complex)
            
def NearNeighb(A, MatBool, itemax = 20):    
    """
    unused TBD
    """
    #MatBool = A != A to get a matrix with booleans for the condition A to be nan
    #bins = array(where(A != A), dtype=int) to get the locations where A is nan
    bins = array(where(MatBool))
    lens4dim=  A.shape    
    dims, Nbins = bins.shape
    ok = ones((2,dims,Nbins),dtype=int)
    neighb = zeros((2,dims,Nbins),dtype=int)
    
    " Identify the type of data you will be playing with "
    datatype = type(A[[[0] for i in range(dims)]][0])
    if datatype == int32 or datatype == int:
        choice = zeros((2,dims,Nbins),dtype=int)
    elif datatype == float64 or datatype == float:
        choice = zeros((2,dims,Nbins),dtype=int)
    else :
        choice = zeros((2,dims,Nbins),dtype=complex)
    
    for n in [0,1]:
        
        ite = 0
        
        " Initialize neighb and choice "
        neighb[n] = bins
        choice[n] = array([A[MatBool]]*dims)
        
        while any(ok.reshape(-1) == 1) and abs(ite) < itemax :
            
            ite += (-1)**n # -1 left neighbours and +1 right neighbours

            for i in range(dims):
                
                " Check whether neighbours' indices are < 0 "
                ok[i, (ok[i] == 1) * (bins[i]+ite  < 0)] = 2 

                " Check whether neighbours' indices are > lens4dim[i]-1 "
                ok[i, (ok[i] == 1) * (bins[i]+ite > lens4dim[i]-1)] = 2

                " Construct a list with the bins' neighbours for ok[i]==1 "
                binslist = [list(bins[ii]) for ii in range(dims)]  
                for iii in range(Nbins):
                    if ok[i,iii] == 1:
                        binslist[i][iii] += ite
                
                choice[n,i,ok[i]==1] = A[binslist][ok[i]==1]
                binslistarray = array(binslist,dtype=int)
                neighb[n,i,ok[i]==1] = binslistarray[i,ok[i]==1]
                
                " Check whether or not the neighbours are nan "
                ok[i, (ok[i]==1)*(A[binslist]==A[binslist])] = 0 # nan == nan --> False
    
    """ 
    - choice[0] right neighbours and choice[1] left neighbours.
    - choice[0,1] right nieghbours varying axis=1 and the variation, i.e. the location of the right neighbours 
    through this particular axis, is stored in neighb[0,1]. Only axis=1 change from the original bins.
    - ok == 0 : non-nan nearest neighbour has been found.
    - ok == 2 : we couldn't go farther right or left
    - ok == 1 : itemax's been reached without finding a non-nan neighbour.
    """           
    return choice, neighb, bins, ok
    
def execute(command):
    """
    unused TBD
    """
    import sys

    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    for c in iter(lambda: process.stdout.read(1), ''):
        sys.stdout.write(c)
#    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#    output = ''
#
#    # Poll process for new output until finished
#    for line in iter(process.stdout.readline, ""):
#        module_logger.info(line),
#        output += line
#
#
#    process.wait()
#    exitCode = process.returncode
#
#    if (exitCode == 0):
#        return output
#    else:
#        raise Exception(command, exitCode, output)
        
def nfr(path, DOF, Nd) :
    """
    unused TBD
    """
    f_CA = open(os.path.join(path,'CA.dat'), 'r')
    Nf = array(f_CA.readline().split(':')[-1], dtype = int)
    Ca = zeros((Nf, DOF, DOF), dtype = float) 
    
    Nlines = int(ceil(DOF/6.))
    
    for f in range(Nf):
        burn = f_CA.readline().split()
        for dof in range(DOF):
            ls_tmp = []
            for nls in range(Nlines):
                ls_tmp += f_CA.readline().split()
                
            Ca[f,dof,:] = array(ls_tmp, dtype = float)
    
    del(burn)
    f_CA.close()
    
    f_CM = open(os.path.join(path,'CM.dat'), 'r')
    Cm = zeros((Ca.shape) , dtype = float) 
    
    burn = f_CM.readline().split(':')[-1]
    
    for f in range(Nf):
        burn = f_CM.readline().split()
        for dof in range(DOF):
            ls_tmp = []
            for nls in range(Nlines):
                ls_tmp += f_CM.readline().split()
                
            Cm[f,dof,:] = array(ls_tmp,dtype = float)
    
    del(burn)
    f_CM.close()
    
    f_Ex = open(os.path.join(path,'ExcitationForce.tec'), 'r')
    Nd = int(Nd)
    Fex = zeros((Nf, Nd, DOF), dtype = complex)
    
    Nlines = int(ceil(((DOF*2)+1)/80.))
    
    for skip_header in range(DOF+1):
        burn = f_Ex.readline()
    
    for d in range(Nd):
        burn = f_Ex.readline()
        for f in range(Nf):
            ls_tmp = []
            for nls in range(Nlines):
                ls_tmp += f_Ex.readline().split()
            
            MagPha = array(ls_tmp[1:],dtype = float)
            Fex[f,d,:] = MagPha[0:-1:2]*exp(1j*MagPha[1::2])
            
    del(burn)
    f_Ex.close()
    
    Fex = conj(Fex)
    
    return (Fex, Cm, Ca)