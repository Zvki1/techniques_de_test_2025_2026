#!/usr/bin/env python3
"""Démonstration visuelle de la triangulation de Delaunay.

Ce script génère une visualisation interactive montrant:
1. Un ensemble de points aléatoires
2. La triangulation de Delaunay calculée par notre algorithme
3. Animation optionnelle du processus
"""

import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from triangulator.triangulation import triangulate


def generate_random_points(n: int, seed: int = None) -> list[tuple[float, float]]:
    """Génère n points aléatoires dans un carré [0, 100] x [0, 100].

    Args:
        n: Nombre de points à générer.
        seed: Graine pour la reproductibilité (optionnel).

    Returns:
        Liste de tuples (x, y).
    """
    if seed is not None:
        random.seed(seed)
    return [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]


def plot_triangulation(points: list[tuple[float, float]],
                       triangles: list[tuple[int, int, int]],
                       title: str = "Triangulation de Delaunay",
                       show_indices: bool = False,
                       save_path: str = None):
    """Affiche la triangulation avec matplotlib.

    Args:
        points: Liste des points (x, y).
        triangles: Liste des triangles (indices).
        title: Titre du graphique.
        show_indices: Afficher les indices des points.
        save_path: Chemin pour sauvegarder l'image (optionnel).
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Couleurs pour les triangles
    colors = plt.cm.Set3(np.linspace(0, 1, len(triangles)))

    # Dessiner les triangles remplis
    for i, tri in enumerate(triangles):
        triangle_points = [points[tri[0]], points[tri[1]], points[tri[2]]]
        polygon = patches.Polygon(triangle_points,
                                  facecolor=colors[i],
                                  edgecolor='darkblue',
                                  linewidth=1.5,
                                  alpha=0.6)
        ax.add_patch(polygon)

    # Dessiner les points
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.scatter(xs, ys, c='red', s=100, zorder=5, edgecolors='darkred', linewidths=2)

    # Afficher les indices si demandé
    if show_indices:
        for i, (x, y) in enumerate(points):
            ax.annotate(str(i), (x, y), textcoords="offset points",
                       xytext=(5, 5), fontsize=10, fontweight='bold')

    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.grid(True, alpha=0.3)

    # Ajouter les statistiques
    stats_text = f"Points: {len(points)} | Triangles: {len(triangles)}"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Image sauvegardée: {save_path}")

    plt.show()


def demo_step_by_step(n_points: int = 10, delay: float = 0.5):
    """Démonstration pas à pas de l'ajout de points.

    Args:
        n_points: Nombre de points à ajouter progressivement.
        delay: Délai entre chaque étape (secondes).
    """
    print(f"\n🎯 Démonstration pas à pas avec {n_points} points\n")

    # Générer tous les points
    all_points = generate_random_points(n_points, seed=42)

    fig, ax = plt.subplots(figsize=(10, 10))
    plt.ion()  # Mode interactif

    for i in range(3, n_points + 1):
        ax.clear()

        current_points = all_points[:i]

        try:
            triangles = triangulate(current_points)

            # Dessiner les triangles
            colors = plt.cm.Pastel1(np.linspace(0, 1, max(len(triangles), 1)))
            for j, tri in enumerate(triangles):
                triangle_pts = [current_points[tri[0]],
                               current_points[tri[1]],
                               current_points[tri[2]]]
                polygon = patches.Polygon(triangle_pts,
                                          facecolor=colors[j % len(colors)],
                                          edgecolor='navy',
                                          linewidth=2,
                                          alpha=0.5)
                ax.add_patch(polygon)
        except ValueError:
            triangles = []

        # Dessiner les points
        xs = [p[0] for p in current_points]
        ys = [p[1] for p in current_points]
        ax.scatter(xs, ys, c='red', s=150, zorder=5,
                  edgecolors='darkred', linewidths=2)

        # Marquer le dernier point ajouté
        if i > 3:
            ax.scatter([current_points[-1][0]], [current_points[-1][1]],
                      c='lime', s=200, zorder=6, edgecolors='green',
                      linewidths=3, marker='*')

        ax.set_xlim(-5, 105)
        ax.set_ylim(-5, 105)
        ax.set_aspect('equal')
        ax.set_title(f"Triangulation de Delaunay - Étape {i-2}/{n_points-2}",
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        stats = f"Points: {len(current_points)} | Triangles: {len(triangles)}"
        ax.text(0.02, 0.98, stats, transform=ax.transAxes,
               fontsize=11, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        plt.pause(delay)

    plt.ioff()
    print("\n✅ Démonstration terminée!")
    plt.show()


def demo_comparison(n_points: int = 20):
    """Compare différentes configurations de points.

    Args:
        n_points: Nombre de points pour chaque configuration.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 14))

    configs = [
        ("Points aléatoires", generate_random_points(n_points, seed=123)),
        ("Points en grille", [(i*20, j*20) for i in range(5) for j in range(4)]),
        ("Points en cercle", [(50 + 40*np.cos(2*np.pi*i/12),
                               50 + 40*np.sin(2*np.pi*i/12)) for i in range(12)]),
        ("Points en spirale", [(50 + (5+i*3)*np.cos(i*0.5),
                                50 + (5+i*3)*np.sin(i*0.5)) for i in range(15)]),
    ]

    for ax, (title, points) in zip(axes.flat, configs):
        try:
            triangles = triangulate(points)

            # Dessiner les triangles
            colors = plt.cm.Set2(np.linspace(0, 1, max(len(triangles), 1)))
            for i, tri in enumerate(triangles):
                tri_pts = [points[tri[0]], points[tri[1]], points[tri[2]]]
                polygon = patches.Polygon(tri_pts,
                                          facecolor=colors[i % len(colors)],
                                          edgecolor='darkblue',
                                          linewidth=1.5,
                                          alpha=0.6)
                ax.add_patch(polygon)
        except ValueError:
            triangles = []

        # Points
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        ax.scatter(xs, ys, c='red', s=80, zorder=5,
                  edgecolors='darkred', linewidths=1.5)

        ax.set_xlim(-5, 105)
        ax.set_ylim(-5, 105)
        ax.set_aspect('equal')
        ax.set_title(f"{title}\n({len(points)} pts, {len(triangles)} tri)",
                    fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

    plt.suptitle("Comparaison des Triangulations de Delaunay",
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig("demo_triangulation.png", dpi=150, bbox_inches='tight')
    print("Image sauvegardée: demo_triangulation.png")
    plt.show()


def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("   🔺 DÉMONSTRATION - Triangulation de Delaunay 🔺")
    print("=" * 60)

    while True:
        print("\nChoisissez une option:")
        print("  1. Triangulation simple (20 points)")
        print("  2. Démonstration pas à pas (animation)")
        print("  3. Comparaison de configurations")
        print("  4. Triangulation personnalisée")
        print("  5. Quitter")

        choice = input("\nVotre choix (1-5): ").strip()

        if choice == "1":
            print("\n🔄 Génération de 20 points aléatoires...")
            points = generate_random_points(20, seed=42)
            triangles = triangulate(points)
            print(f"✅ {len(triangles)} triangles générés!")
            plot_triangulation(points, triangles,
                             title="Triangulation de Delaunay - 20 points",
                             show_indices=True)

        elif choice == "2":
            try:
                n = int(input("Nombre de points (5-30): ") or "15")
                n = max(5, min(30, n))
            except ValueError:
                n = 15
            demo_step_by_step(n_points=n, delay=0.8)

        elif choice == "3":
            demo_comparison()

        elif choice == "4":
            try:
                n = int(input("Nombre de points: ") or "10")
                n = max(3, min(1000, n))
            except ValueError:
                n = 10

            print(f"\n🔄 Génération de {n} points...")
            points = generate_random_points(n)
            triangles = triangulate(points)
            print(f"✅ {len(triangles)} triangles générés!")
            plot_triangulation(points, triangles,
                             title=f"Triangulation de Delaunay - {n} points",
                             show_indices=(n <= 20),
                             save_path=f"triangulation_{n}_points.png")

        elif choice == "5":
            print("\n👋 Au revoir!")
            break

        else:
            print("❌ Option invalide, réessayez.")


if __name__ == "__main__":
    main()
