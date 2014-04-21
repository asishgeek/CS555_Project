#!/usr/bin/python

from uuid import uuid4
from hashlib import md5

class Commit:
  '''
    A class that encapsulates a commitment for a graph, specified as an adjacency matrix
    A particular bit in the graph is committed as: hash(rA, rB, bit)
    For a adjacency matrix of size N x N three matrices of size N x N each are produced:
      1) A commitment matrix which is the hash of all the bits of the adjacency matrix
      2) Two random matrices. One of them is to be kept secret while the other is provided as a guarantee of commitment.
    
    Usage:
      c = Commit(graph) //Creates commitment object
      (commitment, rA) = c.getCommitment() // Gets the commitment and one of the random matrices
      rB = c.revealCommitment(verticesToBeRevealed) // Reveal part of the commitment (i.e. specific elements of the second random matrix)
      verifyCommitment(rA, rB, commitment, graph) //Verify that commitment is indeed valid
  '''

  def __init__(self, graph):
    if not graph or len(graph) <= 0:
      raise Exception('Input should be an adjacency matrix (list of lists).')

    self.__randomA = []
    self.__randomB = []
    self.__commitment = []

    for row in graph:
      r = map(lambda x: (uuid4().hex, uuid4().hex), row)
      r = zip(*r)
      randomA = r[0]
      randomB = r[1]
      com = map(lambda (ra, rb, b): md5('%s,%s,%s'%(ra, rb, b)).hexdigest(), zip(randomA, randomB, row) )
      self.__randomA.append(tuple(randomA))
      self.__randomB.append(tuple(randomB))
      self.__commitment.append(tuple(com))

    self.__commitment = tuple(self.__commitment)
    self.__randomA = tuple(self.__randomA)
    self.__randomB = tuple(self.__randomB)
  

  def getCommitment(self):
    '''
      Returns the commitment matrix and one of the random matrices (randomA)
    '''
    return (self.__commitment, self.__randomA)

  def revealCommitment(self, revealVertices=None):
    ''' 
      If the input graph is None then reveal all the vertices (i.e. return the entire randomB matrix.
      otherwise reveal only those elements of randomB where the corresponding bit in the input graph is 1.
    '''
    if not revealVertices:
      return self.__randomB
    
    index = 0
    revealed = []
    for row in revealVertices:
      revealedRow = map(lambda (b, rB): rB if b == 1 else 0, zip(row, self.__randomB[index]))
      revealed.append(revealedRow)
      index += 1

    return tuple(revealed)

def verifyCommitment(randomA, randomB, commitment, graph):
  '''
    Utility method that
    verifies if the @commitment matrix is indeed produced by hashing @randomA, @randomB and @graph element wise.
    Only non-zero elements of @randomB are checked so that we can verify part of a graph (i.e. only revealed vertices).
  '''
  getHash = lambda ra, rb, b: md5('%s,%s,%s'%(ra, rb, b)).hexdigest()
  for index in range(len(commitment)):
    for (rA, rB, c, b) in zip(randomA[index], randomB[index], commitment[index], graph[index]):
      if rB and getHash(rA, rB, b) != c:
        return False

  return True

def prettyPrintMatrix(mat):
  return "\n".join(map(lambda row: "\t".join(map(str,row)),mat))

def prettyPrintMatrixSpc(mat):
  return "\n".join(map(lambda row: " ".join(map(str,row)),mat))
#  for row in mat:
#    print "%s\n"%("\t".join(map(str, row)))

def _test():
  graph = [
    [1, 1, 0, 0],
    [1, 0, 0, 1],
    [0, 0, 0, 0],
    [0, 1, 0, 0]
  ]  
  com = Commit(graph)
  (commitment, randomA) = com.getCommitment()
  revealMat = [
    [0, 0, 1, 0],
    [1, 0, 0, 1],
    [0, 0, 0, 0],
    [0, 1, 0, 0]
  ]
  randomB = com.revealCommitment(revealMat)
  print verifyCommitment(randomA, randomB, commitment, graph)

