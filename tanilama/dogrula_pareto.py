import sys, torch, copy
sys.path.insert(0, '/home/user/Mucit-ai/mucit_ai_esas/mucit_ai')
from kontratlar import Riyazi_Pareto_PCGrad_MGDA_Operator

torch.manual_seed(0)
sekiller = [(7, 5), (3,), (11, 2), (4, 4)]
n = 5
params = [torch.nn.Parameter(torch.randn(*s)) for s in sekiller]
shardlar = [[torch.randn(*s) for s in sekiller] for _ in range(n)]

op = Riyazi_Pareto_PCGrad_MGDA_Operator()


def eski_referans(shard_gradyanlari, trainable_params, op):
    n = len(shard_gradyanlari)
    duz = [torch.cat([g.reshape(-1).double() for g in sh]) for sh in shard_gradyanlari]
    norm = [float(v.norm().item()) + 1e-8 for v in duz]
    hat = [duz[i] / norm[i] for i in range(n)]
    pc = [h.clone() for h in hat]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dot_ij = float(torch.dot(pc[i], hat[j]).item())
            if dot_ij < 0.0:
                nsq = float(torch.dot(hat[j], hat[j]).item()) + 1e-8
                pc[i] = pc[i] - (dot_ij / nsq) * hat[j]
    G = torch.zeros((n, n), dtype=torch.float64)
    for i in range(n):
        for j in range(n):
            G[i, j] = torch.dot(pc[i], pc[j])
    alpha = op.coz_mgda_pareto_weights(G.float())
    toplam = sum(float(alpha[i].item()) * pc[i] for i in range(n))
    return alpha, toplam


alpha_eski, duz_eski = eski_referans(shardlar, params, op)

params_y = [torch.nn.Parameter(p.detach().clone()) for p in params]
opt = torch.optim.SGD(params_y, lr=0.0)
alpha_yeni = op.birlestir_ve_uygula_dagitik_gradyanlar(
    [[g.clone() for g in sh] for sh in shardlar], params_y, opt, max_norm=1e18
)
duz_yeni = torch.cat([p.grad.reshape(-1).double() for p in params_y])

print('alpha eski :', alpha_eski.tolist())
print('alpha yeni :', alpha_yeni.tolist())
print('alpha maks fark:', float((alpha_eski.double() - alpha_yeni.double().cpu()).abs().max()))
fark = (duz_eski - duz_yeni).abs().max().item()
oran = fark / (duz_eski.abs().max().item() + 1e-30)
print('grad mutlak fark:', fark)
print('grad nispi fark :', oran)
