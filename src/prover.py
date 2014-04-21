import process
import os, sys
from uuid import uuid4
import commit
from commit import Commit
import json

'''
Util Functions
'''
def printUsage():
        print "Usage %s <CommonInputFile> <ProverInputFile>"%sys.argv[0]

'''
Get Read/Write Named Pipes
'''
def getNamedPipes():
	pipeRdName = "/tmp/Verifier"
	pipeWrName = "/tmp/Prover"
	if (not os.path.exists(pipeRdName)):
		os.mkfifo(pipeRdName)
	if (not os.path.exists(pipeWrName)):
		os.mkfifo(pipeWrName)
	pipeRd = open(pipeRdName, 'r')
	pipeWr = os.open(pipeWrName, os.O_WRONLY)
	return pipeRd, pipeWr

'''
Proover Process
'''
def prover():
        # Get Named Pipes
	pipeRd, pipeWr = getNamedPipes()

	if len(sys.argv) != 3:
		printUsage()
		return 1

	# Parse Input Files
	commonInputFile = sys.argv[1]
        proverInputFile = sys.argv[2]
        g1, g2 = process.parse_input_file(commonInputFile)
        subgraphInducer, pi_original = process.parse_prover_input_file(proverInputFile)

	# Exchange Iteration Count and Identifier
	iterCount = int(process.readPipe(pipeRd))
	print "Number of Iterations: %d\n"%iterCount
	uid = process.readPipe(pipeRd).rstrip()

        for iteration in range(0,iterCount):
		# Protocol/Iteration Transcript
		fname = "../transcripts/transcript_prover_iter_%d_%s.txt"%(iteration,uid)
	        fp = open(fname, 'w')
		print "\n\nIteration number " + str(iteration)
        	print "Transcript is being written to file %s"%(fname)

		# Generate random Isomorphism alpha and matrix Q=Alpha(G2)
        	alpha = process.get_random_isomorphism(len(g2))
        	q = process.get_isomorphic_graph(g2, alpha)
		print "Generated Random Isomorphism Alpha"

                # Send Commitment
        	commitQ = Commit(q)
        	(commitmentQ, randomAQ) = commitQ.getCommitment()
        	fp.write("Commitment of matrix Q:\n" + commit.prettyPrintMatrix(commitmentQ) + "\n\n")
        	fp.write("Matrix randomA:\n" + commit.prettyPrintMatrix(randomAQ) + "\n\n")
		process.writePipe(pipeWr, json.dumps(commitmentQ)+"\n")
		process.writePipe(pipeWr, json.dumps(randomAQ)+"\n")
		print "Commited to Q"

                # Get Coin Toss
		coin_toss = process.readPipe(pipeRd).rstrip();
		fp.write("Coint toss Result: " + coin_toss + "\n")
		print "Coin Toss Received '%s'"%coin_toss

                if coin_toss == 'h':
			# Heads
			# Reveal Isomorphism Alpha and secret random commitment matrix randomBQ 
                	randomBQ = commitQ.revealCommitment()
			process.writePipe(pipeWr, json.dumps(alpha)+"\n")                        
			process.writePipe(pipeWr, json.dumps(randomBQ)+"\n")
			fp.write("Revealed Isomorphism alpha \n" + str(alpha) + "\n")
			fp.write("Revealed matrix randomBQ \n" + commit.prettyPrintMatrix(randomBQ) + "\n\n")
			print "Revealed Isomorphism Alpha and secret commitment matrix RandomB"
     
                else:   
			# Tails otherwise
			# Calculate Isomorphism Pi
			pi, qP = process.get_iso_and_iso_subgraph(g1, g2, subgraphInducer, pi_original, alpha, q)
			# Calculate partial secret random commitment matrix randomBQ_partial
            		subgraph_bool_matrix = process.get_boolean_matrix(q, process.apply_iso_on_subgph_indc(subgraphInducer, alpha))
			randomBQ_partial = commitQ.revealCommitment(subgraph_bool_matrix)
			# Send Isomorphism Pi, partial secret random commitment matrix randomBQ_partial and partial subgraph operator
			process.writePipe(pipeWr, json.dumps(pi)+"\n")                        
			process.writePipe(pipeWr, json.dumps(randomBQ_partial)+"\n")                        
			process.writePipe(pipeWr, json.dumps(process.apply_iso_on_subgph_indc(subgraphInducer, alpha)["VD"])+"\n")                        
			fp.write("Revealed Isomorphism Pi \n" + str(pi) + "\n")
			fp.write("Revealed Partial matrix randomBQ_partial \n" + commit.prettyPrintMatrix(randomBQ_partial) + "\n")
			fp.write("Revealed Vertex Deletion Info \n" + str(process.apply_iso_on_subgph_indc(subgraphInducer, alpha)["VD"]) + "\n")
			print "Revealed Subgraph Isomorphism Pi, Partial Random Commitment matrix RandomB and Vertex Deletion Information"

		

if __name__ == "__main__":
	sys.exit(prover());
