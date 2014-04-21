#!/usr/bin/python
import sys
import commit
from  commit import Commit
import whrandom as rand
from uuid import uuid4
import os

def readGraph(cur, text):
    n = int(text[cur].strip())
    g = []
    cur += 1

    for i in range(cur, cur+n):
        g.append(map(int, text[i].strip().split(' ')))

    return i+1, g

def parse_input_file(filename):
    f = open(filename, "r")
    file_txt = f.readlines()
    f.close()
    len_file_txt = len(file_txt)
    cur = 0

    # Parse G1 and G2
    cur, g1 = readGraph(cur, file_txt)
    cur, g2 = readGraph(cur, file_txt)

    return g1, g2


def parse_prover_input_file(filename):
    f = open(filename,"r")
    file_txt = f.readlines()
    f.close()
    len_file_txt = len(file_txt)
    cur=0;
    # Parse the subgraph inducer
    edges_to_delete = [map(int, edge.split(',')) for edge in file_txt[cur].strip().split(' ')[1: ]]
    vertices_to_delete = map(int, file_txt[cur+1].strip().split(' ')[1: ])
    cur += 2

    # Parse the isomorphism
    pi_original = {}
    range_list = file_txt[cur].strip().split(' ')
    for i in range(len(range_list)):
        pi_original[i] = int(range_list[i])

    return {"ER": edges_to_delete, "VD": vertices_to_delete}, pi_original


def get_random_isomorphism(n):
    s = range(n)
    isomorphism = {}
    for i in range(n):
        element = rand.choice(s)
        isomorphism[i] = element
        s.remove(element)

    return isomorphism

def get_isomorphic_graph(g, iso):
    n = len(g)
    gP = [[0] * n for i in range(n)]
    for i in range(n):
        for j in range(n):
            gP[iso[i]][iso[j]] = g[i][j]
    return gP

def apply_iso_on_subgph_indc(si, iso):
    return {
        "VD": [iso[vertex] for vertex in si["VD"]],
        "ER": [[iso[edge[0]], iso[edge[1]]] for edge in si["ER"]]
    }

def get_subgraph(si, g):
    gP = get_isomorphic_graph(g, {i:i for i in range(len(g))})
    er = si["ER"]
    for edge in er:
        gP[edge[0]][edge[1]] = gP[edge[1]][edge[0]] = 0

    si["VD"].sort(reverse=True)
    for vertex in si["VD"]:
        gP.pop(vertex)
        for elements in gP:
            elements.pop(vertex)

    return gP

def get_iso_and_iso_subgraph(g1, g2, si, pi_original, alpha, q):
    qP = get_subgraph(apply_iso_on_subgph_indc(si, alpha), q)

    exduce=[]
    cur=0
    vditer=0
    si["VD"].sort()
    while (vditer<len(si["VD"])):
    	while (cur+vditer<si["VD"][vditer]):
		exduce.append(cur+vditer)
		cur=cur+1
	vditer=vditer+1
    while (cur<len(g1)):
    	exduce.append(cur+vditer)
	cur=cur+1

    range_list = []
    for i in range(len(g1)):
        range_list.append(alpha[exduce[pi_original[i]]])

    pi = {} 
    range_list_sorted = sorted(range_list)
    for i in range(len(range_list)):
        pi[i] = range_list_sorted.index(range_list[i])

    return pi, qP

def get_boolean_matrix(g, si):
    n = len(g)
    bool_matrix = [[True] * n for i in range(n)]
    for edge in si["ER"]:
        bool_matrix[edge[0]][edge[1]] = False
        bool_matrix[edge[1]][edge[0]] = False
    for vertex in si["VD"]:
        for i in range(n):
           bool_matrix[vertex][i] = False
           bool_matrix[i][vertex] = False
    return bool_matrix

#def printUsage():
#  print "Usage: %s <input file>"%sys.argv[0]

def readPipe(pipe):
        return pipe.readline()

def writePipe(pipe, text):
        os.write(pipe, text)

'''
Create Test Cases
'''
def createTestCases(n):
	n=int(n)
	g1 = [[0] * n for i in range(n)]
	for i in range(0,rand.choice(range(n))*rand.choice(range(n))):
    		j=rand.choice(range(n))
    		k=rand.choice(range(n))
		g1[j][k]=g1[k][j]=1
	pi_orig = get_random_isomorphism (len(g1))
	gP = get_isomorphic_graph(g1, pi_orig)
	
	g2 = get_isomorphic_graph(g1, pi_orig)
	si={};
	si["VD"]=[];
	
	for i in range(0,rand.choice(range(n))):
    		j=rand.choice(range(n))
		si["VD"].append(j)
	si["VD"] = list(set(si["VD"]))
	si["VD"].sort(reverse=False);
	for i in si["VD"]:
		g2.insert(i,[0]*len(g2))
		for elements in g2:
			elements.insert(i,0)
			
	si["ER"]=[];
	
	for i in range(0,rand.choice(range(len(g2)))*rand.choice(range(len(g2)))):
    		j=rand.choice(range(len(g2)))
    		k=rand.choice(range(len(g2)))
		if (g2[j][k]==0):
			g2[j][k]=g2[k][j]=1
			si["ER"].append([j,k])
	
        
	fname = "../data/commonInput_%d.txt"%(n)
	fp = open(fname, 'w')
	gname = "../data/proverInput_%d.txt"%(n)
	gp = open(gname, 'w')
 	fp.write("%d\n"%len(g1))
	fp.write(commit.prettyPrintMatrixSpc(g1)+"\n")
 	fp.write("%d\n"%len(g2))
	fp.write(commit.prettyPrintMatrixSpc(g2)+"\n")

	gp.write("ER ")
	for elements in si["ER"]:
		gp.write(str(elements[0])+","+str(elements[1])+" ")
	gp.write("\n")
	gp.write("VD " + " ".join(map(str,si["VD"])) + "\n")
	gp.write(" ".join(map(str,pi_orig.values()))+"\n")

	gp1=get_subgraph(si, g2);
	gp2=get_isomorphic_graph(g1, pi_orig);

	print commit.prettyPrintMatrix(gp1)+"\n"
	print commit.prettyPrintMatrix(gp2)+"\n"
	print commit.prettyPrintMatrix(gP)+"\n"

	return g1,g2,pi_orig,si,gP


if __name__ == "__main__":
   sys.exit(createTestCases(sys.argv[1]))
