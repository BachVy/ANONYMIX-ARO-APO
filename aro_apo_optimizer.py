# aro_apo_optimizer.py
import numpy as np
from utils import fitness_function, space_bound
import logging
from anonymizer import Anonymizer
from scipy.special import gamma 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def levy(dim):
    beta = 1.5
    try:
        sigma = (gamma(1 + beta) * np.sin(np.pi * beta / 2) / (gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
    except Exception:
        sigma = 1.0 # Fallback an toàn nếu gamma lỗi
        
    u = np.random.randn(dim) * sigma
    v = np.random.randn(dim)
    # Tránh chia cho 0
    step = u / (np.abs(v) ** (1 / beta) + 1e-9)
    return step

def aro_apo_optimization(hierarchy_loader, input_file, k, l, c, output_file, **params):
    npop = params.get('npop', 10)
    max_it = params.get('max_it', 50)
    w, u, v = params['w'], params['u'], params['v']
    log_every = params.get('log_every', 10)
    patience = params.get('patience', 5)
    temp_dir = params.get('temp_dir', None) 

    # 1. Khởi tạo không gian tìm kiếm
    dim = len(hierarchy_loader.available_attributes)
    lb = np.zeros(dim, dtype=int)
    ub = np.array([hierarchy_loader.max_levels[attr] for attr in hierarchy_loader.available_attributes], dtype=int)

    # 2. Khởi tạo quần thể ngẫu nhiên
    pop_pos = np.random.randint(lb, ub + 1, size=(npop, dim))
    
    # Tính fitness ban đầu
    pop_fit = np.array([fitness_function(ind, hierarchy_loader, input_file, k, l, c, w, u, v, temp_dir=temp_dir)[0] for ind in pop_pos])

    # Tìm Global Best ban đầu
    best_idx = np.argmin(pop_fit)
    best_f = pop_fit[best_idx]
    best_x = pop_pos[best_idx].copy()
    
    his_best_fit = np.zeros(max_it)
    no_improve = 0
    prev_best = best_f

    # --- VÒNG LẶP TỐI ƯU ---
    for it in range(max_it):
        # A. Giai đoạn ARO (Artificial Rabbits Optimization) - Exploration
        if it % 2 == 0: 
            theta = 2 * (1 - (it + 1) / max_it)
            for i in range(npop):
                L = (np.e - np.exp(((it + 1) / max_it) ** 2)) * np.sin(2 * np.pi * np.random.rand())
                
                # Tạo hướng ngẫu nhiên
                rd = int(np.floor(np.random.rand() * dim))
                rand_dim = np.random.permutation(dim)
                direct1 = np.zeros(dim)
                if rd < dim: direct1[rand_dim[:rd+1]] = 1 # Fix index bounds
                
                R = L * direct1
                A = 2 * np.log(1 / (np.random.rand() + 1e-9)) * theta

                if A > 1:
                    # Detour foraging
                    K = np.delete(np.arange(npop), i)
                    rand_idx = np.random.choice(K)
                    delta = pop_pos[i] - pop_pos[rand_idx]
                    noise = np.round(0.5 * (0.05 + np.random.rand())) * np.random.randn(dim)
                    new_pos = pop_pos[rand_idx] + R * delta + noise
                else:
                    # Random hiding
                    ttt = int(np.floor(np.random.rand() * dim))
                    direct2 = np.zeros(dim); direct2[ttt] = 1
                    H = ((max_it - (it + 1)) / max_it) * np.random.randn()
                    b = pop_pos[i] + H * direct2 * pop_pos[i]
                    new_pos = pop_pos[i] + R * (np.random.rand() * b - pop_pos[i])

                # Kiểm tra biên và cập nhật
                new_pos = space_bound(new_pos, ub, lb).astype(int)
                new_fit, _ = fitness_function(new_pos, hierarchy_loader, input_file, k, l, c, w, u, v, temp_dir=temp_dir)

                if new_fit < pop_fit[i]:
                    pop_pos[i] = new_pos
                    pop_fit[i] = new_fit
                    if new_fit < best_f:
                        best_f = new_fit
                        best_x = new_pos.copy()
        
        # B. Giai đoạn APO (Artificial Protozoa Optimizer) - Exploitation
        else: 
            theta1 = (1 - it / max_it)
            for i in range(npop):
                newPopPos_float = None # Reset biến tạm
                
                # Cập nhật f_attraction (B)
                B = 2 * np.log(1 / (np.random.rand() + 1e-9)) * theta1
                
                if B > 0.5: # Heterotrophic Mode
                    step1_found = False
                    step1 = np.zeros(dim)
                    
                    # Tìm hàng xóm khác biệt để di chuyển tới
                    for _ in range(10): # Giới hạn thử 10 lần thay vì max_it để nhanh hơn
                        K_idx = [j for j in range(npop) if j != i]
                        if not K_idx: break
                        RandInd = np.random.choice(K_idx)
                        step1 = pop_pos[i] - pop_pos[RandInd]
                        if np.linalg.norm(step1) > 1e-9: 
                            step1_found = True
                            break
                    
                    if not step1_found: 
                        # Nếu không tìm được, nhảy ngẫu nhiên nhỏ
                        step1 = np.random.randn(dim) * 0.1

                    R = 0.5 * (0.05 + np.random.rand()) * np.random.normal(0, 1)
                    Y = pop_pos[i] + 0.01 * levy(dim) * step1 + R
                    
                    step2_angle = (np.random.rand() - 0.5) * np.pi
                    S = np.tan(step2_angle)
                    Z = Y * S
                    
                    # Chọn cái tốt hơn giữa Y và Z
                    Y_bound = space_bound(Y, ub, lb).astype(int)
                    Z_bound = space_bound(Z, ub, lb).astype(int)
                    
                    fy, _ = fitness_function(Y_bound, hierarchy_loader, input_file, k, l, c, w, u, v, temp_dir=temp_dir)
                    fz, _ = fitness_function(Z_bound, hierarchy_loader, input_file, k, l, c, w, u, v, temp_dir=temp_dir)
                    
                    if fy < fz: newPopPos_float, final_fit = Y, fy
                    else: newPopPos_float, final_fit = Z, fz

                else: # Autotrophic Mode
                    F = 0.5
                    available_indices = [j for j in range(npop) if j != i]
                    if len(available_indices) >= 3:
                        RandInd = np.random.choice(available_indices, 3, replace=False)
                        step1 = pop_pos[RandInd[1]] - pop_pos[RandInd[2]]
                        
                        if np.random.rand() < 0.5: W = pop_pos[i] + F * step1
                        else: W = pop_pos[i] + F * 0.01 * levy(dim) * step1
                        
                        f_factor = 0.1 * (np.random.rand() - 1) * ((max_it - it) / max_it)
                        Y = (1 + f_factor) * W
                        
                        # Step 2 logic
                        step2 = np.zeros(dim)
                        rand_idx1 = np.random.randint(0, npop)
                        rand_idx2 = np.random.randint(0, npop)
                        step2 = pop_pos[rand_idx1] - pop_pos[rand_idx2]
                        
                        Epsilon = np.random.uniform(0, 1)
                        if np.random.rand() < 0.5: Z = pop_pos[i] + Epsilon * step2
                        else: Z = pop_pos[i] + F * 0.01 * levy(dim) * step2
                        
                        # So sánh W, Y, Z
                        candidates = [W, Y, Z]
                        best_cand_fit = float('inf')
                        best_cand_pos = None
                        
                        for cand in candidates:
                            cand_bound = space_bound(cand, ub, lb).astype(int)
                            f_val, _ = fitness_function(cand_bound, hierarchy_loader, input_file, k, l, c, w, u, v, temp_dir=temp_dir)
                            if f_val < best_cand_fit:
                                best_cand_fit = f_val
                                best_cand_pos = cand
                        
                        newPopPos_float = best_cand_pos
                        final_fit = best_cand_fit
                    else:
                         # Fallback nếu quần thể quá nhỏ
                         newPopPos_float = pop_pos[i]
                         final_fit = pop_fit[i]

                # CẬP NHẬT QUẦN THỂ APO (Logic đã sửa: đảm bảo luôn cập nhật nếu tốt hơn)
                if newPopPos_float is not None:
                    new_pos = space_bound(newPopPos_float, ub, lb).astype(int)
                    # Tính lại fitness chính xác cho vị trí int cuối cùng
                    real_fit, _ = fitness_function(new_pos, hierarchy_loader, input_file, k, l, c, w, u, v, temp_dir=temp_dir)
                    
                    if real_fit < pop_fit[i]:
                        pop_pos[i] = new_pos
                        pop_fit[i] = real_fit
                        if real_fit < best_f:
                            best_f = real_fit
                            best_x = new_pos.copy()

        # --- Ghi Log & Kiểm tra hội tụ ---
        his_best_fit[it] = best_f
        if (it + 1) % log_every == 0 or it == max_it - 1:
            logger.info(f"Loop {it+1}/{max_it} | Best Fitness: {best_f:.6f}")

        if best_f == prev_best:
            no_improve += 1
        else:
            no_improve = 0
            prev_best = best_f

        if no_improve >= patience:
            logger.info(f"Dừng sớm tại vòng {it+1}")
            his_best_fit = his_best_fit[:it+1]
            break

    # 3. Kết xuất kết quả cuối cùng
    anonymizer = Anonymizer(hierarchy_loader)
    gen_levels = {attr: int(lvl) for attr, lvl in zip(hierarchy_loader.available_attributes, best_x)}
    
    _, _, final_k_viol, final_l_viol = anonymizer.anonymize(gen_levels, input_file, k, l, c, output_file)

    max_level = max(hierarchy_loader.max_levels.values()) if hierarchy_loader.max_levels else 1
    info_loss = sum(lvl / max_level for lvl in gen_levels.values()) / len(gen_levels) if gen_levels else 0.0

    return best_x, best_f, his_best_fit, info_loss, final_k_viol, final_l_viol