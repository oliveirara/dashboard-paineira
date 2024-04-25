import os
import re
import tkinter as tk
from tkinter import filedialog, ttk

import matplotlib as mpl
import pandas as pd
from matplotlib import pyplot as plt


def selecionar_diretorio():
    diretorio = filedialog.askdirectory()
    if diretorio:
        entrada_diretorio.delete(0, tk.END)
        entrada_diretorio.insert(0, diretorio)


def mudar_kelvin(T):
    return T + 273.15


def voltar_graus(T):
    return T - 273.15


def arrumar_temp_real(T):
    """Arruma temp para a real

    Args:
        T (float): Temperatura do aquecedor.
    """
    return (T - 85.28) / 1.0593


# def arrumar_temp_aquecedor(T):
#     """Arrumar temp para o aquecedor.

#     Args:
#         T (float): Temperatura real.
#     """


def plotar_dados():
    # Obter entrada do usuário para temperatura mínima, máxima e step.
    MIN_TEMP = float(entrada_temp_min.get())
    MAX_TEMP = float(entrada_temp_max.get())
    STEP_TEMP = float(entrada_step_temp.get())

    # Obter entrada do usuário para os valores mínimos e máximos do eixo x
    X_MIN = float(entrada_x_min.get())
    X_MAX = float(entrada_x_max.get())

    # Obter entrada do usuário para os valores mínimos e máximos do eixo x para detecção de pico
    X_MIN_PICO = float(entrada_x_min_pico.get())
    X_MAX_PICO = float(entrada_x_max_pico.get())

    # Tamanho do ponto
    TAMANHO_PONTO = int(entrada_ponto.get())

    # Unidades
    UNIDADE_TEMP = seletor_unidade_temperatura.get()
    UNIDADE_PLOT = seletor_unidade_plot.get()
    
    # Fonte
    TAMANHO_FONTE = int(entrada_fonte_tamanho.get())
    ESTILO_FONTE = entrada_fonte_estilo.get()

    plt.rcParams.update({'font.size': TAMANHO_FONTE}) 
    
    plt.rcParams.update({'font.family': 'serif', 'font.serif': [ESTILO_FONTE]})
    # Obter diretório selecionado
    diretorio = entrada_diretorio.get()

    # Salvar o gráfico
    salva = True

    # Definir o mapa de cores para plotagem
    cmap = plt.get_cmap("coolwarm")

    # Obter a lista de arquivos no diretório selecionado
    lista_arquivos = os.listdir(diretorio)

    # Inicializar listas vazias para armazenar temperaturas e dataframes
    temperaturas = []
    dfs = []

    # Inicializar uma lista vazia para armazenar os valores máximos de intensidade
    maximos = []

    barra_progresso["maximum"] = len(lista_arquivos)
    rotulo_progresso.config(text="Importando arquivos...")

    calculo_step = 0

    for index, arquivo in enumerate(lista_arquivos, start=1):
        barra_progresso["value"] = index
        barra_progresso.update()

        if arquivo.endswith(".csv"):
            # Extrair a temperatura do nome do arquivo
            temperatura = float(re.search(r"\d+", arquivo.split("_")[-3]).group())

            if UNIDADE_TEMP == "Celsius":
                temperatura = mudar_kelvin(temperatura)
            if temperatura > 401.0208:
                temperatura = arrumar_temp_real(temperatura)
                if UNIDADE_TEMP == "Celsius":
                    temperatura = voltar_graus(temperatura)
            else:
                if UNIDADE_TEMP == "Celsius":
                    temperatura = 25
                else:
                    temperatura = 273.15

            # Verificar se a temperatura está dentro da faixa especificada
            if (MIN_TEMP < temperatura < MAX_TEMP) and (calculo_step <= temperatura):

                calculo_step = temperatura + STEP_TEMP
                if UNIDADE_PLOT == "Celsius" and UNIDADE_TEMP == "Kelvin":
                    temperatura = voltar_graus(temperatura)
                elif UNIDADE_PLOT == "Kelvin" and UNIDADE_TEMP == "Celsius":
                    temperatura = mudar_kelvin(temperatura)
                # Ler o arquivo CSV em um dataframe
                df = pd.read_csv(os.path.join(diretorio, arquivo))

                # Armazenar o valor máximo de intensidade
                maximos.append(df["Intensity"].max())

                temperaturas.append(temperatura)
                dfs.append(df)

    # Ordenar os dados com base nas temperaturas
    pares_ordenados = sorted(zip(temperaturas, dfs), key=lambda x: x[0])

    # Descompactar os pares ordenados em duas listas separadas
    temperaturas, dfs = zip(*pares_ordenados)

    # Definir o intervalo de normalização de cores
    norm = mpl.colors.Normalize(vmin=min(temperaturas), vmax=max(temperaturas))

    # Calcular o valor máximo de intensidade
    maximo = max(maximos) / 3

    x_picos = []
    barra_progresso["maximum"] = len(dfs)
    rotulo_progresso.config(text="Ajustando e analisando picos...")

    for num, df in enumerate(dfs):
        barra_progresso["value"] = num + 1
        barra_progresso.update()

        # Cortar o dataframe usando o X_MIN_PICO e X_MAX_PICO, depois encontrar o ponto máximo
        df_cortado = df[
            (df["2theta (degree)"] >= X_MIN_PICO)
            & (df["2theta (degree)"] <= X_MAX_PICO)
        ]["Intensity"]
        peaks = df_cortado.idxmax()

        # Separar cada curva usando o valor máximo escolhido
        df["Intensity"] = df["Intensity"] + (maximo * num)
        x_picos.append(peaks)

    fig, ax = plt.subplots()
    rotulo_progresso.config(text="Fazendo os plots...")

    for num, df in enumerate(dfs):
        barra_progresso["value"] = num + 1
        barra_progresso.update()

        ax.plot(df["2theta (degree)"], df["Intensity"], c=cmap(norm(temperaturas[num])))

    rotulo_progresso.config(text="Plotando picos...")

    for num, df in enumerate(dfs):
        barra_progresso["value"] = num + 1
        barra_progresso.update()

        ax.plot(
            df["2theta (degree)"].iloc[x_picos[num]],
            df["Intensity"].iloc[x_picos[num]],
            "o",
            markersize=TAMANHO_PONTO,  # Adjust the size of the marker here
            c=cmap(norm(temperaturas[num])),
        )

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  # Você precisa definir um array aqui, mesmo que vazio

    cbar = plt.colorbar(sm, ax=ax)
    if UNIDADE_PLOT == "Kelvin":
        cbar.ax.set_ylabel("Temperatura (K)")
    else:
        cbar.ax.set_ylabel("Temperatura (ºC)")

    ax.set_xlabel("2theta (graus)")
    ax.set_ylabel("Intensidade")
    ax.set_yticks([])
    ax.set_xlim(X_MIN, X_MAX)
    plt.tight_layout()

    rotulo_progresso.config(text="Pronto")
    plt.show()


# Criar janela principal com ThemedTk
root = tk.Tk()
root.title("Gerador de Gráficos")

# Criar frame para entradas
frame_entradas = ttk.Frame(root)
frame_entradas.pack(padx=10, pady=10)

# Seleção de Diretório
rotulo_diretorio = ttk.Label(frame_entradas, text="Selecionar Diretório:")
rotulo_diretorio.grid(row=0, column=0, padx=5, pady=5, sticky="e")

entrada_diretorio = ttk.Entry(frame_entradas)
entrada_diretorio.grid(row=0, column=1, padx=5, pady=5)

botao_selecionar = ttk.Button(
    frame_entradas, text="Procurar", command=selecionar_diretorio
)
botao_selecionar.grid(row=0, column=2, padx=5, pady=5)

# Selecionando unidade
label_unidade_temperatura = ttk.Label(frame_entradas, text="Qual das temperaturas?")
label_unidade_temperatura.grid(row=1, column=0, padx=5, pady=5, sticky="e")

seletor_unidade_temperatura = ttk.Combobox(
    frame_entradas, values=["Kelvin", "Celsius"], state="readonly"
)
seletor_unidade_temperatura.set("Celsius")  # Definindo o valor inicial como Celsius
seletor_unidade_temperatura.grid(row=1, column=1, padx=5, pady=5)

# Entrada de Temperatura Mínima
rotulo_temp_min = ttk.Label(frame_entradas, text="Temperatura Mínima:")
rotulo_temp_min.grid(row=2, column=0, padx=5, pady=5, sticky="e")

entrada_temp_min = ttk.Entry(frame_entradas)
entrada_temp_min.grid(row=2, column=1, padx=5, pady=5)

# Entrada de Temperatura Máxima
rotulo_temp_max = ttk.Label(frame_entradas, text="Temperatura Máxima:")
rotulo_temp_max.grid(row=3, column=0, padx=5, pady=5, sticky="e")

entrada_temp_max = ttk.Entry(frame_entradas)
entrada_temp_max.grid(row=3, column=1, padx=5, pady=5)

# Entrada de Temperatura Máxima
rotulo_step_temp = ttk.Label(frame_entradas, text="Step temperatura:")
rotulo_step_temp.grid(row=4, column=0, padx=5, pady=5, sticky="e")

entrada_step_temp = ttk.Entry(frame_entradas)
entrada_step_temp.grid(row=4, column=1, padx=5, pady=5)

# Entrada de Valor Mínimo do Eixo X
rotulo_x_min = ttk.Label(frame_entradas, text="Valor Mínimo do Eixo X:")
rotulo_x_min.grid(row=5, column=0, padx=5, pady=5, sticky="e")

entrada_x_min = ttk.Entry(frame_entradas)
entrada_x_min.grid(row=5, column=1, padx=5, pady=5)

# Entrada de Valor Máximo do Eixo X
rotulo_x_max = ttk.Label(frame_entradas, text="Valor Máximo do Eixo X:")
rotulo_x_max.grid(row=6, column=0, padx=5, pady=5, sticky="e")

entrada_x_max = ttk.Entry(frame_entradas)
entrada_x_max.grid(row=6, column=1, padx=5, pady=5)

# Entrada de Valor Mínimo do Pico do Eixo X
rotulo_x_min_pico = ttk.Label(frame_entradas, text="Valor Mínimo do Pico do Eixo X:")
rotulo_x_min_pico.grid(row=7, column=0, padx=5, pady=5, sticky="e")

entrada_x_min_pico = ttk.Entry(frame_entradas)
entrada_x_min_pico.grid(row=7, column=1, padx=5, pady=5)

# Entrada de Valor Máximo do Pico do Eixo X
rotulo_x_max_pico = ttk.Label(frame_entradas, text="Valor Máximo do Pico do Eixo X:")
rotulo_x_max_pico.grid(row=8, column=0, padx=5, pady=5, sticky="e")

entrada_x_max_pico = ttk.Entry(frame_entradas)
entrada_x_max_pico.grid(row=8, column=1, padx=5, pady=5)

# Entrada do tamanho do ponto
rotulo_ponto = ttk.Label(frame_entradas, text="Qual o tamanho do ponto:")
rotulo_ponto.grid(row=9, column=0, padx=5, pady=5, sticky="e")

entrada_ponto = ttk.Entry(frame_entradas)
entrada_ponto.insert(0, "5")
entrada_ponto.grid(row=9, column=1, padx=5, pady=5)

# Selecionando unidade
label_unidade_plot = ttk.Label(frame_entradas, text="Qual unidade no gráfico?")
label_unidade_plot.grid(row=10, column=0, padx=5, pady=5, sticky="e")

seletor_unidade_plot = ttk.Combobox(
    frame_entradas, values=["Kelvin", "Celsius"], state="readonly"
)
seletor_unidade_plot.set("Celsius")  # Definindo o valor inicial como Celsius
seletor_unidade_plot.grid(row=10, column=1, padx=5, pady=5)

# Entrada do tamanho da fonte
rotulo_fonte_tamanho = ttk.Label(frame_entradas, text="Tamanho da fonte:")
rotulo_fonte_tamanho.grid(row=11, column=0, padx=5, pady=5, sticky="e")

entrada_fonte_tamanho = ttk.Entry(frame_entradas)
entrada_fonte_tamanho.insert(0, "12")
entrada_fonte_tamanho.grid(row=11, column=1, padx=5, pady=5)

#Qual fonte
rotulo_fonte_estilo = ttk.Label(frame_entradas, text="Qual fonte:")
rotulo_fonte_estilo.grid(row=12, column=0, padx=5, pady=5, sticky="e")

entrada_fonte_estilo = ttk.Entry(frame_entradas)
entrada_fonte_estilo.insert(0, "Times New Roman")
entrada_fonte_estilo.grid(row=12, column=1, padx=5, pady=5)


# Botão Plotar
botao_plotar = ttk.Button(frame_entradas, text="Plotar Dados", command=plotar_dados)
botao_plotar.grid(row=13, column=0, columnspan=2, pady=10)


# Barra de Progresso
frame_progresso = ttk.Frame(root)
frame_progresso.pack(padx=15, pady=(0, 10))

barra_progresso = ttk.Progressbar(
    frame_progresso, orient="horizontal", mode="determinate"
)
barra_progresso.pack(fill="x", padx=5, pady=5)

rotulo_progresso = ttk.Label(frame_progresso, text="")
rotulo_progresso.pack(pady=(0, 5))

root.mainloop()
