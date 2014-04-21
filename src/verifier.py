import process
import os, sys
from uuid import uuid4
import commit
from commit import Commit
import json

'''
Util Functions
'''
def cleanDict(d):
	return {int(k):int(v) for k,v in d.items()}

def printUsage():
	print "Usage %s <CommonInputFile>"%sys.argv[0]

'''
Get Read/Write Named Pipes
'''
def getNamedPipes():
	pipeRdName = "/tmp/Prover"
	pipeWrName = "/tmp/Verifier"
	if (not os.path.exists(pipeRdName)):
		os.mkfifo(pipeRdName)
	if (not os.path.exists(pipeWrName)):
		os.mkfifo(pipeWrName)
	pipeWr = os.open(pipeWrName, os.O_WRONLY)
	pipeRd = open(pipeRdName, 'r')
	return pipeRd, pipeWr

'''
Verifier Process
'''
def verifier():
	# Get Named Pipes
	pipeRd, pipeWr = getNamedPipes()

	if len(sys.argv) != 2:
		printUsage()
		return 1

	# Parse Input Files
	commonInputFile = sys.argv[1]
	g1, g2 = process.parse_input_file(commonInputFile)
	
	# Exchange Iteration Count and Identifier
	iterCount=int(raw_input('Enter Number of Iterations: '))
	process.writePipe(pipeWr, "%d\n"%iterCount)
	uid = uuid4().hex
	process.writePipe(pipeWr, "%s\n"%uid)

	for iteration in range(0,iterCount):
		# Protocol/Iteration Transcript
		fname = "../transcripts/transcript_verifier_iter_%d_%s.txt"%(iteration,uid)
                fp = open(fname, 'w')
                print "\n\nIteration number " + str(iteration+1)
                print "Transcript is being written to file %s"%(fname)

		# Receive Commitment
		commitmentQ = json.loads(process.readPipe(pipeRd).rstrip())		
		randomAQ = json.loads(process.readPipe(pipeRd).rstrip())		
                fp.write("Commitment of matrix Q:\n" + commit.prettyPrintMatrix(commitmentQ) + "\n\n")
                fp.write("Matrix randomA:\n" + commit.prettyPrintMatrix(randomAQ) + "\n\n")
                print "Received Commitment for Q"
		
		# Toss a Coin
		coin_toss = raw_input("Say H(ead)/T(tail):  ").strip()[0].lower()
		process.writePipe(pipeWr, "%s\n"%coin_toss)
                fp.write("Coint toss Result: " + coin_toss + "\n")
                print "Coin Toss Sent '%s'"%coin_toss

		if coin_toss == 'h':
			# Heads
			# Receive Isomorphism Alpha and secret random commitment matrix randomBQ
			alpha = cleanDict(json.loads(process.readPipe(pipeRd).rstrip()))		
			randomBQ = json.loads(process.readPipe(pipeRd).rstrip())
			# Check: Commitment(Q) matches Q=Alpha(G2)
			check = commit.verifyCommitment(randomAQ, randomBQ, commitmentQ, process.get_isomorphic_graph(g2, alpha))		
			fp.write("Received Isomorphism alpha \n" + str(alpha) + "\n")
                        fp.write("Received matrix randomBQ \n" + commit.prettyPrintMatrix(randomBQ) + "\n\n")
                        print "Received Isomorphism Alpha and secret commitment matrix RandomB"

		else:	
			# Tails otherwise
			# Receive Isomorphism Pi, partial secret random commitment matrix randomBQ_partial and partial subgraph operator
			pi = cleanDict(json.loads(process.readPipe(pipeRd).rstrip()))		
			randomBQ_partial = json.loads(process.readPipe(pipeRd).rstrip())		
			# Only Vertex Deletion Information is sent in the subgraph operator, the edge removal information is hidden to ensure zero-knowledge
			si={"ER":[]}
			si["VD"] = json.loads(process.readPipe(pipeRd).rstrip())
			# Check: Commitment(Subgraph(Q)) matches Q'=Pi(G1)
			check = commit.verifyCommitment(process.get_subgraph(si, randomAQ), process.get_subgraph(si, randomBQ_partial), process.get_subgraph(si, commitmentQ), process.get_isomorphic_graph(g1, pi))
			fp.write("Received Isomorphism Pi \n" + str(pi) + "\n")
                        fp.write("Received Partial matrix randomBQ_partial \n" + commit.prettyPrintMatrix(randomBQ_partial) + "\n")
                        fp.write("Received Vertex Deletion Info \n" + str(si["VD"]) + "\n")
                        print "Received Subgraph Isomorphism Pi, Partial Random Commitment matrix RandomB and Vertex Deletion Information"


		if (not check):
			fp.write("Check Failed\n")
			print("Check Failed\n")
			break
		else:	
			fp.write("Check Succeded\n")
			print("--------Check Successful---------")
			print("---------------------------------")
			print "Probability that Prover knows the Subgraph: %0.4f\n\n"%(100*(1.0-(1.0/2**(iteration+1))))


if __name__ == "__main__":
	sys.exit(verifier());
