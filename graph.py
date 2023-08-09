from uuid import uuid4
from collections import deque

class Graph:
    def __init__(self):
        self.vertices = 0
        self.edges = []
    
    def add_vertex(self):
        self.vertices += 1
    
    def set_vertices(self, vertices):
        self.vertices = vertices
        for i, edge in enumerate(self.edges):
            source, target = edge
            if (source >= vertices or target >= vertices):
                self.edges.pop(i)
    
    def add_edge(self, source, target, weight = 1):
        if (weight > 0):
            self.edges.append((source, target, weight))
    
    def delete_edge(self, source, target):
        for i, edge in enumerate(self.edges):
            edge_source, edge_target, _ = edge
            if (edge_source == source and edge_target == target):
                self.edges.pop(i)
                break
 
    def get_vertices_count(self):
        return self.vertices
    
    def get_edges_count(self):
        return len(self.edges)
    
    def get_degrees(self):
        degrees = []
        for vertex in range(self.vertices):
            degrees.append(0)
            for source, target, weight in self.edges:
                if (source == vertex or target == vertex):
                    degrees[vertex] += weight * 2 if target == source else weight
        return degrees
    
    def get_adjacency_matrix(self):
        matrix = []
        for source in range(self.vertices):
            matrix.append([])
            for target in range(self.vertices):
                matrix[source].append(0)
        for source, target, weight in self.edges:
            matrix[source][target] = weight
        return matrix
    
    def get_cut_vertices(self):
        cut_vertices = []
        for vertex in range(self.vertices):
            _, edges = self.pop_vertex(vertex)
            if not self.is_connected_2(vertex):
                cut_vertices.append(vertex)
            self.add_vertex()
            for edge in edges:
                source, target, weight = edge
                self.add_edge(source, target, weight)
        return cut_vertices
    
    def pop_vertex(self, vertex):
        edges = []
        new_edges = []
        if vertex < self.vertices:
            for i, edge in enumerate(self.edges):
                source, target, weight = edge
                if source == vertex or target == vertex:
                    edges.append((source, target, weight))
                else:
                    new_edges.append((source, target, weight))

            self.edges = new_edges
            self.vertices = self.vertices - 1
        return (vertex, edges)

    
    def get_bridges(self):
        bridges = []
        for i, edge in enumerate(self.edges):
            source, target, weight = edge
            self.delete_edge(source, target)
            if not self.is_connected():
                bridges.append((source, target))
            self.edges.insert(i, (source, target, weight))
        return bridges

    def is_connected(self):
        visited = [False] * self.vertices
        self.dfs(0, visited)
        return all(visited)
    
    def is_connected_2(self, vertex):
        visited = [False] * (self.vertices + 1)
        visited[vertex] = True
        self.dfs(vertex + 1 if vertex < self.vertices else vertex - 1, visited)
        return all(visited)

    def dfs(self, vertex, visited):
        visited[vertex] = True
        for source, target, _ in self.edges:
            if (source == vertex or target == vertex) and not visited[source if target == vertex else target]:
                self.dfs(source if target == vertex else target, visited)