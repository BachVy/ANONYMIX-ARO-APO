# utils.py
import os
import numpy as np
import random
import logging
from anonymizer import Anonymizer
from classifier import calculate_accuracy
from config import TRAIN_TEST_DIR

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_info_loss(generalization_levels, hierarchy_loader):
    levels = list(generalization_levels.values())
    if not levels: return 0.0
    max_level = max(hierarchy_loader.max_levels.values()) if hierarchy_loader.max_levels else 1
    return sum(level / max_level for level in levels) / len(levels)

def fitness_function(X, hierarchy_loader, input_file, k, l, c, w, u, v, output_file=None, temp_dir=None):
    """
    Tính Fitness với tham số c cho Recursive Diversity.
    """
    X = X.astype(int)
    gen_levels = {attr: int(level) for attr, level in zip(hierarchy_loader.available_attributes, X)}
    anonymizer = Anonymizer(hierarchy_loader)

    # 1. Tính Accuracy (Utility)
    if output_file and os.path.exists(output_file):
        accuracy_after = calculate_accuracy(output_file)
    else:
        # QUAN TRỌNG: Sử dụng temp_dir được truyền vào, nếu không mới dùng mặc định
        target_dir = temp_dir if temp_dir else TRAIN_TEST_DIR
        temp_file = os.path.join(target_dir, "temp_anonymized.csv")
        
        anonymizer.anonymize(gen_levels, input_file, k, l, c, temp_file)
        try:
            accuracy_after = calculate_accuracy(temp_file)
        except:
            accuracy_after = 0.0
        
        if os.path.exists(temp_file):
            try: os.remove(temp_file)
            except: pass

    # 2. Tính Privacy Cost (K và L violations)
    _, min_k, k_viol, l_viol = anonymizer.anonymize(gen_levels, input_file, k, l, c)
    
    total_violations = k_viol + l_viol
    info_loss = calculate_info_loss(gen_levels, hierarchy_loader)
    
    fitness = w * info_loss + u * total_violations + v * (1 - accuracy_after)
    return fitness, info_loss

def space_bound(X, ub, lb):
    return np.clip(X, lb, ub)

def get_final_metrics(best_x, hierarchy_loader, input_file, k, l, c, output_file):
    best_x = best_x.astype(int)
    anonymizer = Anonymizer(hierarchy_loader)
    gen_levels = {attr: int(lvl) for attr, lvl in zip(hierarchy_loader.available_attributes, best_x)}
    _, _, final_k_viol, final_l_viol = anonymizer.anonymize(gen_levels, input_file, k, l, c, output_file)
    max_level = max(hierarchy_loader.max_levels.values()) if hierarchy_loader.max_levels else 1
    info_loss = sum(lvl / max_level for lvl in gen_levels.values()) / len(gen_levels) if gen_levels else 0.0
    return info_loss, final_k_viol, final_l_viol

# ==========================================
# CÁC THUẬT TOÁN SO SÁNH (GA & PSO)
# ==========================================

def genetic_algorithm_optimization(hierarchy_loader, input_file, k, l, c, output_file, **params):
    npop = params.get('npop', 20)
    max_it = params.get('max_it', 50)
    log_every = params.get('log_every', 10)
    patience = params.get('patience', 10)
    temp_dir = params.get('temp_dir', None) # <--- LẤY TEMP_DIR
    mutation_rate = 0.1
    w, u, v = params['w'], params['u'], params['v']

    dim = len(hierarchy_loader.available_attributes)
    lb = np.zeros(dim, dtype=int)
    ub = np.array([hierarchy_loader.max_levels[attr] for attr in hierarchy_loader.available_attributes], dtype=int)

    def crossover(parent1, parent2):
        if len(parent1) < 2: return parent1.copy(), parent2.copy()
        pt = random.randint(1, len(parent1) - 1)
        c1 = np.concatenate((parent1[:pt], parent2[pt:]))
        c2 = np.concatenate((parent2[:pt], parent1[pt:]))
        return c1, c2

    def mutate(individual):
        ind = individual.copy()
        for i in range(len(ind)):
            if random.random() < mutation_rate:
                ind[i] = random.randint(lb[i], ub[i])
        return ind

    population = np.random.randint(lb, ub + 1, size=(npop, dim))
    # Truyền temp_dir vào
    pop_fit = np.array([fitness_function(ind, hierarchy_loader, input_file, k, l, c, w, u, v, temp_dir=temp_dir)[0] for ind in population])

    best_idx = np.argmin(pop_fit)
    best_x = population[best_idx].copy()
    best_f = pop_fit[best_idx]
    
    history = []
    no_improve = 0
    prev_best = best_f

    for it in range(max_it):
        history.append(best_f)
        if (it + 1) % log_every == 0 or it == max_it - 1:
            print(f"GA Loop {it+1}/{max_it} | Fitness: {best_f:.6f}")

        parents = []
        for _ in range(npop):
            opts = np.random.choice(npop, 3, replace=False)
            winner = opts[np.argmin(pop_fit[opts])]
            parents.append(population[winner])
        
        next_pop = []
        for i in range(0, npop, 2):
            p1, p2 = parents[i], parents[(i+1)%npop]
            c1, c2 = crossover(p1, p2)
            next_pop.extend([mutate(c1), mutate(c2)])
        
        population = np.array(next_pop[:npop])
        # Truyền temp_dir vào
        pop_fit = np.array([fitness_function(ind, hierarchy_loader, input_file, k, l, c, w, u, v, temp_dir=temp_dir)[0] for ind in population])
        
        curr_best_idx = np.argmin(pop_fit)
        if pop_fit[curr_best_idx] < best_f:
            best_f = pop_fit[curr_best_idx]
            best_x = population[curr_best_idx].copy()

        if best_f == prev_best: no_improve += 1
        else: no_improve = 0; prev_best = best_f
        
        if no_improve >= patience:
            print(f"GA dừng sớm tại vòng {it+1}")
            break
            
    info_loss, k_viol, l_viol = get_final_metrics(best_x, hierarchy_loader, input_file, k, l, c, output_file)
    return best_x, best_f, history, info_loss, k_viol, l_viol

def pso_optimization(hierarchy_loader, input_file, k, l, c, output_file, **params):
    npop = params.get('npop', 20)
    max_it = params.get('max_it', 50)
    log_every = params.get('log_every', 10)
    patience = params.get('patience', 10)
    temp_dir = params.get('temp_dir', None) # <--- LẤY TEMP_DIR
    w_params, u, v = params['w'], params['u'], params['v']

    dim = len(hierarchy_loader.available_attributes)
    lb = np.zeros(dim); ub = np.array([hierarchy_loader.max_levels[attr] for attr in hierarchy_loader.available_attributes], dtype=float)

    pop_pos = np.random.uniform(lb, ub, (npop, dim))
    pop_vel = np.random.uniform(-1, 1, (npop, dim))
    
    # Truyền temp_dir vào
    pop_fit = np.array([fitness_function(np.round(ind), hierarchy_loader, input_file, k, l, c, w_params, u, v, temp_dir=temp_dir)[0] for ind in pop_pos])

    pbest_pos = pop_pos.copy(); pbest_fit = pop_fit.copy()
    gbest_idx = np.argmin(pop_fit); gbest_pos = pop_pos[gbest_idx].copy(); gbest_fit = pop_fit[gbest_idx]

    inertia_w = 0.9 - 0.5 * (np.arange(max_it) / max_it)
    c1 = 2; c2 = 2
    history = []
    no_improve = 0; prev_best = gbest_fit

    for it in range(max_it):
        history.append(gbest_fit)
        if (it + 1) % log_every == 0 or it == max_it - 1:
            print(f"PSO Loop {it+1}/{max_it} | Fitness: {gbest_fit:.6f}")

        for i in range(npop):
            r1, r2 = np.random.rand(dim), np.random.rand(dim)
            pop_vel[i] = (inertia_w[it] * pop_vel[i] + c1 * r1 * (pbest_pos[i] - pop_pos[i]) + c2 * r2 * (gbest_pos - pop_pos[i]))
            pop_pos[i] = space_bound(pop_pos[i] + pop_vel[i], ub, lb)
            
            # Truyền temp_dir vào
            current_fit, _ = fitness_function(np.round(pop_pos[i]), hierarchy_loader, input_file, k, l, c, w_params, u, v, temp_dir=temp_dir)
            
            if current_fit < pbest_fit[i]: pbest_fit[i] = current_fit; pbest_pos[i] = pop_pos[i].copy()
            if current_fit < gbest_fit: gbest_fit = current_fit; gbest_pos = pop_pos[i].copy()

        if gbest_fit == prev_best: no_improve += 1
        else: no_improve = 0; prev_best = gbest_fit
        
        if no_improve >= patience:
            print(f"PSO dừng sớm tại vòng {it+1}")
            break

    best_x = np.round(gbest_pos).astype(int)
    info_loss, k_viol, l_viol = get_final_metrics(best_x, hierarchy_loader, input_file, k, l, c, output_file)
    return best_x, gbest_fit, history, info_loss, k_viol, l_viol