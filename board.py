import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_rotated_game_board():
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for i, player in enumerate(["Player 1", "Player 2"]):
        y_offset = 6 if i == 0 else 0  # Player 1 on top, Player 2 on bottom
        rotation = 180 if i == 0 else 0  # Rotate Player 1's Half Board
        
        # Draw Half Board
        ax.add_patch(patches.Rectangle((1, y_offset), 8, 2, edgecolor="black", facecolor="lightblue", lw=2))
        
        # Add Player Label
        ax.text(5, y_offset + 1, f"{player}'s Half Board", ha="center", va="center", 
                fontsize=12, fontweight="bold", rotation=rotation)
        
        # Main Zone
        ax.add_patch(patches.Rectangle((4, y_offset + 1.2), 2, 0.8, edgecolor="black", facecolor="lightgreen", lw=2))
        ax.text(5, y_offset + 1.6, "Main Zone", ha="center", va="center", fontsize=10, rotation=rotation)
        
        # Row (Sub Zones Placeholder)
        ax.add_patch(patches.Rectangle((3, y_offset + 0.2), 4, 0.8, edgecolor="black", facecolor="lightyellow", lw=2))
        ax.text(5, y_offset + 0.6, "Row (Sub Zones)", ha="center", va="center", fontsize=10, rotation=rotation)
        
        # Deck
        ax.add_patch(patches.Rectangle((8.5, y_offset + 0.5), 0.8, 1, edgecolor="black", facecolor="white", lw=2))
        ax.text(8.9, y_offset + 1, "Deck", ha="center", va="center", fontsize=9, rotation=90 + rotation)
        
        # Graveyard
        ax.add_patch(patches.Rectangle((8.5, y_offset + 1.7), 0.8, 0.6, edgecolor="black", facecolor="gray", lw=2))
        ax.text(8.9, y_offset + 2, "Graveyard", ha="center", va="center", fontsize=9, rotation=90 + rotation)
    
    # General Layout Settings
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')  # Turn off the axis
    
    # Title
    plt.title("Rotated Game Board Layout", fontsize=16, fontweight="bold", pad=20)
    plt.show()

draw_rotated_game_board()