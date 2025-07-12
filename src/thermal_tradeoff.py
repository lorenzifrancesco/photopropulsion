import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import simulation
from pydantic import BaseModel
import tomllib  # Use 'import tomli' for Python < 3.11
import pandas as pd
import os

class ThermalConfig(BaseModel):
    n_samples    : int
    cutoff_low   : float 
    cutoff_high  : float 
    p_0          : float 
    q_0          : float
    d_sail       : float
    t_f          : float

compute = True
plot_finals = False

# Load TOML
with open("input/_thermal_tradeoff.toml", "rb") as f:
    data = tomllib.load(f)

cf = ThermalConfig(**data)
print(cf)
cmap = plt.get_cmap('Set1')
figsize = (4.2, 1.8)

cutoff_frequencies = np.linspace(cf.cutoff_low, cf.cutoff_high, cf.n_samples)  # Normalized to Nd:YAG

if not plot_finals:
        
    output = "results/"
    l = simulation.Launch()
    l.multilayer = simulation.Reflector.M1

    l.alpha2 = 1.0
    l.mode = "delay"
    l.p_0 = cf.p_0
    l.t_f = cf.t_f
    # 3e6 for short, 3e9 for long. Medium: 1e9
    l.q_0 = cf.q_0
    l.d_sail = cf.d_sail
    l.compile()

    P_list = []
    q_list = []
    Q_list = []
    T_list = []

    for cutoff_frequency in cutoff_frequencies:
        l.cutoff_frequency = cutoff_frequency
        l.file = f'cutoff_{cutoff_frequency:.2f}.csv'
        if compute:
            l.write_config('input/_config.toml')
            l.run()
            # l.plot_dynamics(na = f'_{cutoff_frequency:.2f}')
        # l.plot_spectrum(threshold=0.001, na = f'_{cutoff_frequency:.2f}')
        dd = pd.read_csv('results/' + l.file)
        P_list.append(dd['P'])
        q_list.append(dd['q'])
        Q_list.append(dd['Q'])
        T_list.append(dd['T'])
        print(f"cut: {cutoff_frequency:>10} | max Q: {np.max(dd['Q']):>10}, max T: {np.max(dd['T']):>10}")

    Q_max = [np.max(Q) for Q in Q_list]
    T_max = [np.max(T) for T in T_list]

    fig, ax1 = plt.subplots(figsize=figsize)
    color1 = 'tab:blue'
    ax1.plot(cutoff_frequencies, Q_max, marker='o', linestyle='-', markersize = 4, color=color1, label='Max Q')
    ax1.set_ylabel(r'$\Delta v/c$', color=color1)
    ax1.set_ylim(0, 1.1 * np.max(Q_list))
    ax1.tick_params(axis='y', labelcolor=color1)

    ax1.set_xlabel(r'$\omega_c/\omega_0$')
    # ax1.ticklabel_format(style='sci', axis='x', scilimits=(3, 0))

    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.plot(cutoff_frequencies, T_max, marker='d', linestyle='--', markersize = 4, color=color2, label='T_max')
    ax2.set_ylim(0, 2000)
    ax2.set_ylabel(r'$T$ [K]', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    # Optional: add grid or a combined legend
    # ax1.grid(True)
    # Combine legends from both axes if needed
    # lines, labels = ax1.get_legend_handles_labels()
    # lines2, labels2 = ax2.get_legend_handles_labels()
    # ax1.legend(lines + lines2, labels + labels2, loc='best')
    plt.tight_layout()
    name = 'media/tradeoff_Q_T.pdf'
    plt.savefig(name)
    print(f"Saved plot to {name}")

    df = pd.DataFrame({
        'v_final': Q_max,
        'temp'+str() : T_max
    })
    print("Q_max_near.append(np.array("+ repr(Q_max)+")")
    print("T_max_near.append(np.array("+ repr(T_max)+")")
    print(df)

    # # save the data to csv
    # df.to_csv('results/tradeoff/tradeoff_Q_T'+cf.q_0+'.csv', index=False)

    # # load all the csv and plot and save the plots
    # tradeoff_folder = 'results/tradeoff/'
    # for file in sorted(os.listdir(tradeoff_folder)):
    #     if file.endswith('.csv'):
    #         df = pd.read_csv(tradeoff_folder + file)
    #         cutoff_frequency = float(file.split('_')[1].split('.')[0])
    #         plt.plot(cutoff_fre,df['v_final'], label=f'cutoff {cutoff_frequency:.2f}')
    #         plt.plot(df['temp'], label=f'T_max {cutoff_frequency:.2f}')
else:
    """ parameters used for the final plot
    n_samples = 10
    cutoff_low = 0.01
    cutoff_high = 0.99
    d_sail = 30
    t_f = 500 # s
    """
    Q_max_near = []
    T_max_near = []
    Q_max_far = []
    T_max_far = []
    # 50e9, 3e9 (far), 2.5e-6 (low engineering /2)
    # Q_max_far.append(
    # np.array([0.1735253329521206, 0.1735253329521206, 0.1735253329521206, 0.1735230199167815, 0.1734856050948989, 0.1728854331984618, 0.1659182335255572, 0.1488726635009245, 0.1246610088942675, 0.0811819862249199]))
    # T_max_far.append(
    # np.array([9119.594857389528, 9119.594857389528, 9119.594857389528, 1759.303479209455, 1759.303479209455, 1573.774668242473, 762.0310683275751, 508.34027236329695, 478.4915712214432, 361.6389585297633]))
    # 50e9, 3e9 (far), 2.5e-6 (zero engineering /1)
    Q_max_far.append(np.array([0.1735254784808314, 0.1735254784808314, 0.1735254784808314, 0.1735231651812499, 0.1734857458589061, 0.172885539038685, 0.1659182620674382, 0.1488726741598456, 0.1246610194555098, 0.0811819947839029]))
    T_max_far.append(np.array([9347.637383366093, 9347.637383366093, 9347.637383366093, 2757.3701308163318, 2757.3701308163318, 2416.2151433331705, 1015.674754006999, 637.3946625952501, 594.7354701933932, 439.5697514626938]))
    # 50e9, 3e9 (far), 5e-6 (high engineering /2)
    Q_max_far.append(np.array([0.1735252141298902, 0.1735252141298902, 0.1735252141298902, 0.173522901522017, 0.1734854901384432, 0.1728853469665523, 0.1659182076207647, 0.1488726552012824, 0.1246610009129655, 0.0811819794183736]))
    T_max_far.append(np.array([8935.382012664377, 8935.382012664377, 8935.382012664377, 1224.246236303076, 804.6167908725251, 747.5338168601608, 447.842605045808, 323.02998297995833, 306.64937802854604, 238.1901480580792]))
    # 50e9, 3e6 (near), 2.5e-5 (zero engineering /1)
    Q_max_near.append(np.array([0.1705684528480331, 0.1705684528379419, 0.1705684110834616, 0.1705668175378431, 0.1705373513345517, 0.1695532970492619, 0.1617574661306776, 0.1455404993637313, 0.1220558388097849, 0.0816822287504918]))
    T_max_near.append(np.array([4655.963206939126, 4655.879171234909, 4505.408552698555, 3521.041659980742, 3521.041659980742, 1642.4910005673205, 1513.2233762857377, 1465.7774779849017, 1247.1308667620117, 451.71618287098215]))
    # 50e9, 3e6 (near), 5e-6 (high engineering /10)
    Q_max_near.append(
    np.array([0.1705682365972099, 0.1705682365871218, 0.1705681949057228, 0.1705666023566457, 0.1705371397313208, 0.1695531433854589, 0.161757421056213, 0.1455404803876736, 0.1220558206714597, 0.0816822133133854]))
    T_max_near.append(
    np.array([4232.863973921145, 4232.779022966124, 4080.647091645429, 923.7466355319864, 923.7466355319864, 598.4073414720685, 571.725383343767, 560.599942053701, 508.7002814952307, 244.097981674867]))
    for i in [0, 1]:
        if i == 0:
            Q_max = Q_max_near
            T_max = T_max_near
            case = 'near'
        else:
            Q_max = Q_max_far
            T_max = T_max_far
            case = 'far'
        fig, ax1 = plt.subplots(figsize=figsize)
        color1 = 'tab:blue'
        ax1.plot(cutoff_frequencies, Q_max[0], marker='o', linestyle='-', markersize = 4, color=color1, label='Max Q')
        ax1.plot(cutoff_frequencies, Q_max[1], marker='o', linestyle='-', markersize = 4, color=color1, label='Max Q')
        ax1.set_ylabel(r'$\Delta v/c$', color=color1)
        ax1.set_ylim(0, 0.2)
        ax1.tick_params(axis='y', labelcolor=color1)

        # Shared x-axis
        ax1.set_xlabel(r'$\omega_c/\omega_0$')
        # ax1.ticklabel_format(style='sci', axis='x', scilimits=(3, 0))

        # T_max_high = 
        # Second axis: T_max
        ax2 = ax1.twinx()
        color2 = 'tab:red'

        ax2.plot(cutoff_frequencies, T_max[0], marker='d', linestyle='--', markersize=4, color=color2, label='T_max')
        ax2.plot(cutoff_frequencies, T_max[1], marker='d', linestyle='--', markersize=4, color=color2, label='T_max')
        ax2.fill_between(cutoff_frequencies, T_max[0], T_max[1], color=color2, alpha=0.3)
        ax2.axhline(1000, ls=":", color="gray")
        ax2.set_ylim(0, 2000)
        ax2.set_ylabel(r'$T$ [K]', color=color2)
        ax2.tick_params(axis='y', labelcolor=color2)
        ax2.ticklabel_format(style='sci', axis='y', scilimits=(3, 0))
        plt.tight_layout()
        name = 'media/combined_tradeoff_Q_T_'+case+'.pdf'
        plt.savefig(name)
        print(f"Saved plot to {name}")