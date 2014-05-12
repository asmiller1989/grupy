#!/usr/bin/python
import os
import sys

## append path to grupy modules
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append( os.path.join( cwd, "..") )



from grupy import *
from grupy.qe import *
from grupy.sym import *
from optparse import OptionParser
import subprocess as sub




# should eventually write some flags for bad data input
## From input file
##################

dir, sg, in_path = GetInput()




## Parse options to graph data and to make/run q2r.in and matdyn.in scripts 
###########################################################################

parser = OptionParser()
parser.set_defaults( 
					 make_scripts = False, 
					 run_scripts = False,
					 bands = False)


parser.add_option("--make", dest="make_scripts", action="store_true")
parser.add_option("--run", dest="run_scripts", action="store_true")
parser.add_option("--bands", dest="bands", action="store_true")

(options, args) = parser.parse_args() 





#### grupy_in object
####################
Gin = grupy_in(dir, in_path, None , sg, None, None, None, None, None, None, None, None)


Gin.prefix = GetPrefix( Gin.dir )
Gin.path, Gin.hs_points = MakePath( Gin.in_path )




(Gin.nat, Gin.V, Gin.m) = GetNat_M_V( Gin.dir, Gin.prefix)

if options.make_scripts:
	MakeMatdyn( Gin.dir, Gin.prefix, Gin.path, Gin.m)
	MakeQ2r(Gin.prefix, Gin.dir)
	print "\nq2r.in and matdyn.in files created\n"
	sys.exit()

# this doesn't work - I need to write a shell script
if options.run_scripts:
	
	for i in range(len(Gin.dir) ):
		
    	q = 'cd %s && q2r.x < q2r.in && cd ..'%(Gin.dir[i])
        sub.call( q , shell=True)

        m = 'cd %s && matdyn.x < matdyn.in && cd ..'%(Gin.dir[i])
        sub.call( m , shell=True)
		
		print "dynamical matrix files created"
	sys.exit()
	
	



## don't need to run GruCalc unless calculating gruneisen
## waste of time to do it this way --  change it

Gin.BZ_path, BZ_labels = MakeBZPath( Gin.hs_points, Gin.path)

q, Darray = ReadDynMat ( Gin.nat, Gin.m, Gin.dir)

Gin.q, gru_data = GruCalc ( Gin, q, Darray)


	
if not options.bands:
	Gout = grupy_out( Gin.prefix, BZ_labels , gru_data   )
	
#
# for some reason it won't write the last data point on tacc
# and therefore the last label won't post
# fix this
#	
	WriteGrupyFile(Gout)
	print "\ngrupy.out file written\n"



### need to feed in new BZ_path
if options.bands:
	bands = GetBands( Gin )
	Gout = grupy_out( Gin.prefix, BZ_labels , bands   )
	WriteBands( Gout, Gin.dir)
	print "\ngrupy.bands.out file written\n"

