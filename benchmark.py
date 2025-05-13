import pygame
import os
import time
import csv
import sys
import matplotlib.pyplot as plt

# Import các thuật toán và hàm cần thiết từ game.py
from game import (
    bfs_algorithm, astar_algorithm, simple_hill_climbing_algorithm,
    partially_observable_algorithm, min_conflicts_algorithm, q_learning_algorithm,
    load_maps_from_file, ROWS, COLS
)

pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Benchmark Tool")

font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 36)

ALGORITHMS = [
    ("BFS", bfs_algorithm),
    ("A*", astar_algorithm),
    ("Simple Hill Climbing", simple_hill_climbing_algorithm),
    ("Partially Observable", partially_observable_algorithm),
    ("Min Conflicts", min_conflicts_algorithm),
    ("Q-Learning", q_learning_algorithm)
]

maps = load_maps_from_file()
map_names = list(maps.keys())

def draw_text(text, x, y, color=(255,255,255), font=font):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

def run_benchmark(algorithm, map_data, n_runs=3):
    results = []
    for run in range(n_runs):
        maze = [row[:] for row in map_data]
        player_pos = (1, 1)
        princess_pos = None
        target_pos = None
        for r in range(ROWS):
            for c in range(COLS):
                if maze[r][c] == 2:
                    princess_pos = (r, c)
                if maze[r][c] == 3:
                    target_pos = (r, c)
        visible = [[True for _ in range(COLS)] for _ in range(ROWS)]
        ai_knowledge = None
        steps = 0
        steps_to_princess = 0
        steps_finish = 0
        found_princess = False
        found_exit = False
        t0 = time.time()
        t_princess = None
        t_exit = None
        max_steps = 300
        for _ in range(max_steps):
            if player_pos == princess_pos and not found_princess:
                found_princess = True
                t_princess = time.time()
                steps_to_princess = steps
            if found_princess and player_pos == target_pos:
                found_exit = True
                t_exit = time.time()
                steps_finish = steps
                break
            # PO cần knowledge đặc biệt
            if algorithm[0] == "Partially Observable":
                if ai_knowledge is None:
                    ai_knowledge = {
                        "maze": [[None for _ in range(COLS)] for _ in range(ROWS)],
                        "probability": [[0.5 for _ in range(COLS)] for _ in range(ROWS)],
                        "visited": set(),
                        "frontier": set(),
                        "princess_found": False,
                        "exit_found": False,
                        "princess_pos": None,
                        "exit_pos": None,
                        "princess_rescued": False,
                        "exploration_bias": 0.3,
                        "visibility_percentage": 50,
                        "fog_enabled": True
                    }
            next_pos, ai_knowledge = algorithm[1](maze, player_pos, princess_pos, target_pos, visible, ai_knowledge)
            steps += 1
            if next_pos == player_pos:
                break
            player_pos = next_pos
            if player_pos == princess_pos:
                ai_knowledge["princess_rescued"] = True
            if ai_knowledge and ai_knowledge.get("princess_rescued", False):
                princess_pos = player_pos
        t1 = time.time()
        results.append({
            "steps": steps,
            "steps_finish": steps_finish if found_exit else steps,
            "steps_to_princess": steps_to_princess if found_princess else steps,
            "time_to_princess": (t_princess-t0) if t_princess else t1-t0,
            "time_to_exit": (t_exit-t_princess) if (t_princess and t_exit) else 0,
            "total_time": (t_exit-t0) if (t_exit and t0) else t1-t0,
            "success": found_exit
        })
    return results

def calc_stats(results):
    stats = {}
    for algo in ALGORITHMS:
        name = algo[0]
        algo_results = [r for r in results if r["algorithm"] == name]
        if not algo_results:
            continue
        n = len(algo_results)
        avg_steps = sum(r["steps"] for r in algo_results) / n
        avg_steps_to_princess = sum(r["steps_to_princess"] for r in algo_results) / n
        avg_steps_finish = sum(r["steps_finish"] for r in algo_results) / n
        avg_time_to_princess = sum(r["time_to_princess"] for r in algo_results) / n
        avg_time_to_exit = sum(r["time_to_exit"] for r in algo_results) / n
        avg_total_time = sum(r["total_time"] for r in algo_results) / n
        success_rate = sum(1 for r in algo_results if r["success"]) / n
        stats[name] = {
            "avg_steps": avg_steps,
            "avg_steps_to_princess": avg_steps_to_princess,
            "avg_steps_finish": avg_steps_finish,
            "avg_time_to_princess": avg_time_to_princess,
            "avg_time_to_exit": avg_time_to_exit,
            "avg_total_time": avg_total_time,
            "success_rate": success_rate
        }
    return stats

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def save_stats_csv(stats, map_name):
    folder = os.path.join(BASE_DIR, "benchmark")
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"benchmark_stats_{map_name}_{int(time.time())}.csv")
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Algorithm", "Avg Steps", "Avg Steps to Princess", "Avg Steps Finish",
            "Avg Time to Princess", "Avg Time to Exit", "Avg Total Time", "Success Rate"
        ])
        for algo, s in stats.items():
            writer.writerow([
                algo, f"{s['avg_steps']:.2f}", f"{s['avg_steps_to_princess']:.2f}", f"{s['avg_steps_finish']:.2f}",
                f"{s['avg_time_to_princess']:.3f}", f"{s['avg_time_to_exit']:.3f}",
                f"{s['avg_total_time']:.3f}", f"{s['success_rate']*100:.1f}%"
            ])

def save_stats_plot(stats, map_name):
    import numpy as np
    folder = os.path.join(BASE_DIR, "benchmark")
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"benchmark_stats_{map_name}_{int(time.time())}.png")
    algos = list(stats.keys())
    avg_steps = [stats[a]["avg_steps"] for a in algos]
    avg_total_time = [stats[a]["avg_total_time"] for a in algos]
    success_rate = [stats[a]["success_rate"]*100 for a in algos]

    x = np.arange(len(algos))
    width = 0.28

    fig, ax1 = plt.subplots(figsize=(11,6))
    ax2 = ax1.twinx()

    # Bar cho Avg Steps
    bars1 = ax1.bar(x - width/2, avg_steps, width, color='#4FC3F7', label='Avg Steps')
    # Bar cho Success Rate
    bars2 = ax2.bar(x + width/2, success_rate, width, color='#81C784', alpha=0.7, label='Success Rate (%)')
    # Line cho Avg Total Time
    line = ax2.plot(x, avg_total_time, color='#FF9800', marker='o', linewidth=2, label='Avg Total Time (s)')

    # Nhãn giá trị trên cột
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{height:.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10, color='#1565C0')
    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f'{height:.0f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10, color='#388E3C')

    ax1.set_ylabel('Avg Steps', color='#1565C0', fontsize=12)
    ax2.set_ylabel('Success Rate (%) / Avg Total Time (s)', color='#388E3C', fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(algos, fontsize=12)
    ax1.set_ylim(0, max(avg_steps + [1]) * 1.2)
    ax2.set_ylim(0, 110)

    plt.title(f"Stats on map: {map_name}", fontsize=15, fontweight='bold')
    # Gộp legend
    lines_labels = [ax.get_legend_handles_labels() for ax in [ax1, ax2]]
    handles, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    ax1.legend(handles, labels, loc='upper left', fontsize=11)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def main():
    selected_map = 0
    n_runs = 3
    running = True
    benchmark_results = []
    show_results = False
    stats = {}
    save_message = ""
    while running:
        screen.fill((30, 30, 40))

        # Khung chọn map
        pygame.draw.rect(screen, (40, 80, 40), (100, 80, 350, 250), border_radius=12)
        draw_text("Map:", 120, 100, (0, 255, 255), big_font)
        for i, name in enumerate(map_names):
            color = (0, 255, 255) if i == selected_map else (200, 200, 200)
            draw_text(f"{i+1}. {name}", 140, 150 + i*30, color)

        draw_text(f"Runs: {n_runs} (UP/DOWN)", 120, 360)

        # Nút RUN ALL ALGORITHMS
        pygame.draw.rect(screen, (200,100,50), (600, 120, 250, 70), border_radius=8)
        draw_text("RUN ALL", 620, 140, (0,0,0), big_font)
        # Nút SAVE RESULTS
        pygame.draw.rect(screen, (50,50,200), (600, 220, 250, 70), border_radius=8)
        draw_text("SAVE", 620, 240, (255,255,255), big_font)

        if show_results and stats:
            draw_text("Algorithm", 120, 420, (255,215,0), font)
            draw_text("Avg Steps", 260, 420, (255,215,0), font)
            draw_text("Avg Steps to Princess", 370, 420, (255,215,0), font)
            draw_text("Avg Steps Finish", 590, 420, (255,215,0), font)
            draw_text("Avg Time to Princess", 720, 420, (255,215,0), font)
            draw_text("Avg Time to Exit", 900, 420, (255,215,0), font)
            draw_text("Success Rate", 1100, 420, (255,215,0), font)
            for idx, (algo, s) in enumerate(stats.items()):
                y = 460 + idx*32
                draw_text(algo, 120, y)
                draw_text(f"{s['avg_steps']:.2f}", 260, y)
                draw_text(f"{s['avg_steps_to_princess']:.2f}", 370, y)
                draw_text(f"{s['avg_steps_finish']:.2f}", 590, y)
                draw_text(f"{s['avg_time_to_princess']:.3f}s", 720, y)
                draw_text(f"{s['avg_time_to_exit']:.3f}s", 900, y)
                draw_text(f"{s['success_rate']*100:.1f}%", 1100, y)
        if save_message:
            draw_text(save_message, 600, 320, (0,255,0), font)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Chọn map bằng phím F1-F9 (hoặc phím 1-9 nếu ít map)
                if pygame.K_F1 <= event.key <= pygame.K_F9:
                    idx = event.key - pygame.K_F1
                    if idx < len(map_names):
                        selected_map = idx
                if pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    if idx < len(map_names):
                        selected_map = idx
                if event.key == pygame.K_UP:
                    n_runs += 1
                if event.key == pygame.K_DOWN and n_runs > 1:
                    n_runs -= 1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Chọn map bằng chuột
                if 100 <= x <= 450 and 150 <= y <= 150 + len(map_names)*30:
                    idx = (y - 150) // 30
                    if 0 <= idx < len(map_names):
                        selected_map = idx
                # RUN ALL ALGORITHMS
                if 600 <= x <= 850 and 120 <= y <= 190:
                    benchmark_results = []
                    for algo_name, algo_func in ALGORITHMS:
                        results = run_benchmark((algo_name, algo_func), maps[map_names[selected_map]], n_runs)
                        for r in results:
                            r["algorithm"] = algo_name
                            r["map"] = map_names[selected_map]
                            benchmark_results.append(r)
                    stats = calc_stats(benchmark_results)
                    show_results = True
                # SAVE STATS & PLOT
                if 600 <= x <= 850 and 220 <= y <= 290 and stats:
                    save_stats_csv(stats, map_names[selected_map])
                    save_stats_plot(stats, map_names[selected_map])
                    save_message = "Đã lưu file CSV và ảnh vào benchmark!"
        pygame.time.delay(50)

if __name__ == "__main__":
    main()