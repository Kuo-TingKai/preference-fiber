import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import random

class FibrationBundle:
    def __init__(self, base_nodes=6, fibration_levels=3, fiber_height=5):
        """
        Initialize a fibration bundle with Z-valued fibers
        
        Parameters:
        base_nodes: number of nodes in base space (graph)
        fibration_levels: number of different fibration levels
        fiber_height: height of the fiber visualization
        """
        self.G = nx.DiGraph()
        self.fiber_height = fiber_height
        self.connections = {}  # Store connection maps between fibers
        
        # Define market goods as node names
        self.market_goods = [
            "iPhone",
            "MacBook",
            "iPad",
            "AirPods",
            "Apple Watch",
            "iMac",
            "Mac mini",
            "Apple TV",
            "HomePod",
            "AirTag"
        ]
        
        # Create base space (graph) with fibration levels
        self.create_base_space(min(base_nodes, len(self.market_goods)), fibration_levels)
        # Create connections between fibers
        self.create_connections()
        
    def create_base_space(self, n_nodes, fibration_levels):
        """Create the base space as a directed graph with fibration levels"""
        # Assign random fibration values to nodes
        self.fibrations = {}
        selected_goods = random.sample(self.market_goods, n_nodes)
        
        for i, good_name in enumerate(selected_goods):
            self.fibrations[good_name] = random.randint(0, fibration_levels-1)
            self.G.add_node(good_name)
        
        # Create edges ensuring partial order
        for good1 in self.G.nodes():
            for good2 in self.G.nodes():
                if good1 != good2 and self.fibrations[good1] > self.fibrations[good2]:
                    self.G.add_edge(good1, good2)
        
        nx.set_node_attributes(self.G, self.fibrations, 'fibration')

    def create_connections(self):
        """Create connection maps between fibers that respect partial ordering"""
        for edge in self.G.edges():
            source, target = edge
            # Always use positive multiplier to preserve order
            multiplier = 1
            # Shift should respect the partial order:
            # if source has higher fibration, shift should be positive
            if self.fibrations[source] > self.fibrations[target]:
                shift = random.randint(0, 2)  # Only positive shifts
            else:
                shift = random.randint(-2, 0)  # Only negative shifts
            self.connections[edge] = {
                'multiplier': multiplier,
                'shift': shift
            }

    def fiber_map(self, edge, z):
        """Apply connection map to a point in the fiber"""
        conn = self.connections[edge]
        return conn['multiplier'] * z + conn['shift']

    def visualize(self):
        """Visualize the fiber bundle with arrows and labeled nodes"""
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Get layout for base space with adjusted parameters
        pos = nx.spring_layout(self.G, k=1, iterations=50)
        
        # Scale the positions to spread them out more
        scale_factor = 2.0
        pos = {node: (coord[0] * scale_factor, coord[1] * scale_factor) 
               for node, coord in pos.items()}
        
        # Draw base space with arrows
        for edge in self.G.edges():
            source, target = edge
            x = [pos[source][0], pos[target][0]]
            y = [pos[source][1], pos[target][1]]
            z = [0, 0]
            
            ax.quiver(x[0], y[0], z[0],
                     x[1]-x[0], y[1]-y[0], z[1]-z[0],
                     color='k', alpha=0.3, 
                     arrow_length_ratio=0.1,  # 減小箭頭大小
                     linewidth=0.8)  # 減小線條寬度
        
        # Add node labels in base space
        for node, (x, y) in pos.items():
            ax.text(x, y, 0, node, 
                   fontsize=8, 
                   horizontalalignment='center',
                   verticalalignment='bottom')
        
        z_points = np.arange(1, self.fiber_height + 1)
        
        # Draw fibers
        for node in self.G.nodes():
            x = pos[node][0]
            y = pos[node][1]
            ax.plot([x]*len(z_points), [y]*len(z_points), z_points, 
                   'b-', alpha=0.5)
            ax.scatter([x]*len(z_points), [y]*len(z_points), z_points, 
                      c='b', s=20)
        
        # Draw connections
        for edge in self.G.edges():
            source, target = edge
            for z in z_points[::2]:
                x1, y1 = pos[source]
                x2, y2 = pos[target]
                z2 = self.fiber_map(edge, z)
                
                dx = x2 - x1
                dy = y2 - y1
                dz = z2 - z
                ax.quiver(x1, y1, z,
                         dx, dy, dz,
                         color='r', alpha=0.2, 
                         arrow_length_ratio=0.1,  # 保持一致的箭頭大小
                         linewidth=0.8)  # 保持一致的線條寬度
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Level')
        ax.set_title('Market Goods Preference Fiber Bundle')
        
        ax.set_xticks([])
        ax.set_yticks([])
        
        ax.set_zticks(z_points)
        ax.set_zticklabels([str(int(z)) for z in z_points])
        
        ax.view_init(elev=20, azim=45)
        
        plt.show()

    def check_compatibility(self):
        """Check if connections satisfy compatibility conditions"""
        for node in self.G.nodes():
            # Get all paths of length 2 starting from this node
            for path in nx.all_simple_paths(self.G, node, cutoff=2):
                if len(path) == 3:
                    # Check composition of connections
                    edge1 = (path[0], path[1])
                    edge2 = (path[1], path[2])
                    # Test some points
                    for z in range(-5, 6):
                        z1 = self.fiber_map(edge1, z)
                        z2 = self.fiber_map(edge2, z1)
                        # Direct connection
                        direct_edge = (path[0], path[2])
                        if direct_edge in self.connections:
                            z_direct = self.fiber_map(direct_edge, z)
                            if abs(z2 - z_direct) > 1e-10:
                                return False
        return True

# Create and visualize the fiber bundle
bundle = FibrationBundle(base_nodes=6, fibration_levels=3, fiber_height=5)
bundle.visualize()

# Check if the connections are compatible
is_compatible = bundle.check_compatibility()
print(f"Bundle connections are compatible: {is_compatible}")