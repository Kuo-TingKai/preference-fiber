import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import random

class FibrationBundle:
    def __init__(self, base_nodes=6, fibration_levels=3, fiber_height=5, connection_params=None, market_goods=None):
        """
        Initialize a fibration bundle with Z-valued fibers
        
        Parameters:
        base_nodes: number of nodes in base space (graph)
        fibration_levels: number of different fibration levels
        fiber_height: height of the fiber visualization
        connection_params: configuration for connection mappings
        market_goods: optional list of market goods to use
        """
        self.G = nx.DiGraph()
        self.fiber_height = fiber_height
        self.connections = {}
        
        self.connection_params = {
            'a': 1.0,
            'type': 'linear'
        } if connection_params is None else connection_params
        
        # Use provided market goods list or default to original list
        self.market_goods = market_goods if market_goods is not None else [
            "iPhone", "MacBook", "iPad", "AirPods", "Apple Watch",
            "iMac", "Mac mini", "Apple TV", "HomePod", "AirTag"
        ]
        
        self.create_base_space(min(base_nodes, len(self.market_goods)), fibration_levels)
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
        
        # Add additional node attributes
        for good_name in selected_goods:
            self.G.nodes[good_name]['name'] = good_name
            self.G.nodes[good_name]['level'] = self.fibrations[good_name]
            self.G.nodes[good_name]['fiber_range'] = range(self.fiber_height + 1)

    def create_connections(self):
        """Create connection maps between fibers that respect partial ordering"""
        for edge in self.G.edges():
            source, target = edge
            # Use linear coefficient from parameters
            a = self.connection_params.get('a', 1.0)
            
            # Determine shift based on fibration levels
            if self.fibrations[source] > self.fibrations[target]:
                b = random.randint(0, 2)  # Positive shift for higher to lower
            else:
                b = random.randint(-2, 0)  # Negative shift for lower to higher
            
            self.connections[edge] = {
                'a': a,  # Linear coefficient
                'b': b,  # Translation value
                'type': self.connection_params.get('type', 'linear'),
                'connection_type': 'standard'
            }
            # Add edge attributes
            self.G.edges[edge].update(self.connections[edge])

    def fiber_map(self, edge, z):
        """Apply connection map to a point in the fiber"""
        conn = self.connections[edge]
        # Linear mapping: φ_e(z) = az + b_e
        return conn['a'] * z + conn['b']

    def visualize(self):
        """Visualize the fiber bundle with arrows and labeled nodes"""
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Adjust spring layout parameters for better node distribution
        pos = nx.spring_layout(
            self.G, 
            k=2.0,           # Increased repulsion (from 1.0 to 2.0)
            iterations=100,   # More iterations for better convergence
            seed=42          # Fixed seed for consistent layout
        )
        
        # Increase scale factor for wider spread
        scale_factor = 3.0   # Increased from 2.0 to 3.0
        pos = {node: (coord[0] * scale_factor, coord[1] * scale_factor) 
               for node, coord in pos.items()}
        
        # Draw base space with arrows (increased transparency)
        for edge in self.G.edges():
            source, target = edge
            x = [pos[source][0], pos[target][0]]
            y = [pos[source][1], pos[target][1]]
            z = [0, 0]
            
            ax.quiver(x[0], y[0], z[0],
                     x[1]-x[0], y[1]-y[0], z[1]-z[0],
                     color='k', alpha=0.15,
                     arrow_length_ratio=0.1,
                     linewidth=0.6)
        
        # Add node labels with adjusted position and style
        for node, (x, y) in pos.items():
            # Add small random offset to label positions to reduce overlap
            offset_x = random.uniform(-0.1, 0.1)
            offset_y = random.uniform(-0.1, 0.1)
            
            ax.text(x + offset_x, y + offset_y, 0, node, 
                   fontsize=9,
                   horizontalalignment='center',
                   verticalalignment='bottom',
                   weight='bold',
                   bbox=dict(facecolor='white', 
                            alpha=0.7,
                            edgecolor='none',
                            pad=1))  # Add white background to labels
        
        z_points = np.arange(1, self.fiber_height + 1)
        
        # Draw fibers
        for node in self.G.nodes():
            x = pos[node][0]
            y = pos[node][1]
            ax.plot([x]*len(z_points), [y]*len(z_points), z_points, 
                   'b-', alpha=0.5)
            ax.scatter([x]*len(z_points), [y]*len(z_points), z_points, 
                      c='b', s=20)
        
        # Draw connections with higher transparency
        for edge in self.G.edges():
            source, target = edge
            for z in z_points[::3]:
                x1, y1 = pos[source]
                x2, y2 = pos[target]
                z2 = self.fiber_map(edge, z)
                
                dx = x2 - x1
                dy = y2 - y1
                dz = z2 - z
                ax.quiver(x1, y1, z,
                         dx, dy, dz,
                         color='r', alpha=0.1,
                         arrow_length_ratio=0.1,
                         linewidth=0.6)
        
        # Adjust plot limits to ensure all nodes are visible
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Level')
        ax.set_title('Market Goods Preference Fiber Bundle')
        
        # Increase axis limits to prevent clipping
        x_min = min(coord[0] for coord in pos.values())
        x_max = max(coord[0] for coord in pos.values())
        y_min = min(coord[1] for coord in pos.values())
        y_max = max(coord[1] for coord in pos.values())
        
        margin = 1.0  # Add margin around the plot
        ax.set_xlim(x_min - margin, x_max + margin)
        ax.set_ylim(y_min - margin, y_max + margin)
        
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
                    direct_edge = (path[0], path[2])
                    
                    if direct_edge in self.connections:
                        # Test points in fiber range
                        for z in range(-5, 6):
                            # Composite mapping
                            z1 = self.fiber_map(edge1, z)
                            z2 = self.fiber_map(edge2, z1)
                            # Direct mapping
                            z_direct = self.fiber_map(direct_edge, z)
                            # Check compatibility with tolerance
                            if abs(z2 - z_direct) > 1e-10:
                                return False
        return True

# Create a much larger fiber bundle with more nodes
extra_large_connection_params = {
    'a': 1.5,
    'type': 'linear'
}

# Extended market goods list
extra_market_goods = [
    "iPhone", "MacBook", "iPad", "AirPods", "Apple Watch",
    "iMac", "Mac mini", "Apple TV", "HomePod", "AirTag",
    "Magic Keyboard", "Magic Mouse", "Pro Display XDR",
    "Apple Pencil", "Smart Keyboard", "MagSafe Charger",
    "AirPods Max", "Mac Pro", "Studio Display", "Apple Care+"
]

# Create only one large bundle example
extra_large_bundle = FibrationBundle(
    base_nodes=20,          # Using maximum available nodes
    fibration_levels=5,     # More hierarchical levels
    fiber_height=8,         # Higher fibers
    connection_params=extra_large_connection_params,
    market_goods=extra_market_goods
)

# Visualize the extra large bundle
plt.figure(figsize=(20, 16))  # Increased figure size for better visibility
extra_large_bundle.visualize()

# Print bundle statistics
print("\nExtra Large Bundle Statistics:")
print(f"Number of nodes: {extra_large_bundle.G.number_of_nodes()}")
print(f"Number of edges: {extra_large_bundle.G.number_of_edges()}")

# Print detailed level distribution
print("\nFibration levels distribution:")
level_dist = {}
for node in extra_large_bundle.G.nodes():
    level = extra_large_bundle.G.nodes[node]['level']
    level_dist[level] = level_dist.get(level, 0) + 1
for level, count in sorted(level_dist.items()):
    print(f"Level {level}: {count} nodes")

# Calculate and print additional metrics
avg_out_degree = sum(dict(extra_large_bundle.G.out_degree()).values()) / extra_large_bundle.G.number_of_nodes()
print(f"\nAverage out-degree: {avg_out_degree:.2f}")

# Print connection statistics
print("\nConnection Parameters Distribution:")
connection_stats = {
    'a_values': [],
    'b_values': []
}
for edge, data in extra_large_bundle.G.edges(data=True):
    connection_stats['a_values'].append(data['a'])
    connection_stats['b_values'].append(data['b'])

print(f"Average linear coefficient (a): {np.mean(connection_stats['a_values']):.2f}")
print(f"Average translation value (b): {np.mean(connection_stats['b_values']):.2f}")