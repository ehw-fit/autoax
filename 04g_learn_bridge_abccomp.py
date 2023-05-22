#!/usr/bin/env python3
# %%%
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

from sklearn import linear_model
from sklearn import neighbors
from sklearn import neural_network
from sklearn import kernel_ridge
from sklearn import gaussian_process
from sklearn import cross_decomposition
from sklearn import naive_bayes
from sklearn import ensemble
from sklearn import isotonic
from sklearn import svm
from sklearn.ensemble import RandomForestRegressor

# %%%

df_random = pd.read_pickle("data/all_random.pkl.gz").query("qp==37")
df_lib = pd.read_pickle("components/data/circ.lib.pkl.gz")
df_abc = pd.read_pickle("components/data/circ.abc.pkl.gz")
df_lib = pd.merge(df_lib, df_abc[["file", "abc_power"]], on="file")

# make mean of two benchmarks

def issame(x):
    #print(x)
    first = x.iloc[0]
    if np.all(x == first):
        return first
    return None
aggf = {x: issame if x == "mcm" or df_random[x].dtype == np.dtype("O") else "mean" for x in df_random.columns}
df_random = df_random.query("benchmark=='bridge-close'").groupby("configuration").agg(aggf)


# %%%

def do_learn(df_random: pd.DataFrame, df_lib: pd.DataFrame, mcm: int, x_params=["bddavg", "bddmax"], y_param="total_psnr_yuv"):
    # prepare X set
    dfr = df_random.query("mcm == @mcm").dropna(axis="columns", how="all")

    x_columns = []
    for c in dfr.columns:
        if not c.startswith("dct_") and not c.startswith(f"c{mcm}_"):
            print("skip", c, f"mcm{mcm}_")
            continue

        dfr = dfr.merge(
            df_lib[["cfun"] +
                   x_params].rename(columns={x: f"{c}_{x}" for x in x_params}),
            left_on=c, right_on="cfun", suffixes=("", f"_{c}"))
        x_columns += [f"{c}_{x}" for x in x_params]

    dfr = dfr.dropna(subset=["configuration"] + x_columns + [y_param])
    

    corr_out = []


    for reg, regname in [
        (ensemble.RandomForestRegressor(n_estimators=100), "rforest"),
        (linear_model.BayesianRidge(), "bayes"),
        (svm.SVR(), "svm"),
    ]:
        df_train = dfr.head(int(0.8 * len(dfr)))
        df_test = dfr.tail(len(dfr) - len(df_train))

        reg.fit(df_train[x_columns], df_train[y_param])

        t_train = reg.predict(df_train[x_columns])
        t_test = reg.predict(df_test[x_columns])

        df_train.insert(0, "est", t_train)
        df_test.insert(0, "est", t_test)

       
        corr_test = df_test[["est", y_param]].corr().loc["est", y_param]
        corr_train = df_train[["est", y_param]].corr().loc["est", y_param]
        print("corr test:", y_param, regname, corr_test)
        print("corr train:", y_param, regname, corr_train)
        
        corr_d = {
            "mcm": mcm,
            "regname": regname,
            "y_param": y_param,
            "train_shape": df_train[x_columns].shape,
            "x_params" : x_columns
        }
        corr_out.append({**corr_d, "kind": "test", "corr": corr_test})
        corr_out.append({**corr_d, "kind": "train", "corr": corr_train})
        # corr_out.append(
        #     ";".join([circ, regname, "test", values, str(corr_test)]))
        # corr_out.append(
        #     ";".join([circ, regname, "train", values, str(corr_train)]))

        joblib.dump(
            reg, f'reg/bridge-abccomp-regressor.{regname}.mcm{mcm}_{y_param}.joblib')

        plt.figure(figsize=(12, 8))

        #for fid, values in enumerate(df_train_all):
    
        plt.subplot(111 + 0)
        plt.title(f"{regname} - {y_param}")

        plt.scatter(df_test[y_param],
                    df_test["est"], label="test", s=2)
        plt.scatter(df_train[y_param],
                    df_train["est"], label="train", s=2)

        plt.xlabel(y_param + " (real)")
        plt.ylabel(y_param + " (est)")
        plt.legend()

        plt.savefig(f"plt/bridge-abccomp-regressor.{regname}.{mcm}_{y_param}.png")
        plt.close()
    return corr_out

if __name__ == "__main__":


    df_corr = []
    for mcm in [1, 2, 3, 4]:
        df_corr += do_learn(df_random=df_random, df_lib=df_lib, mcm=mcm)
        df_corr += do_learn(df_random=df_random, df_lib=df_lib, mcm=mcm, x_params=["fpga_power"], y_param="power")
    df_corr = pd.DataFrame(df_corr)
    df_corr.to_csv("reg/bridge-abccomp-corr_random.csv")
    df_corr.to_pickle("reg/bridge-abccomp-corr_random.pkl.gz")
    #do_learn(circ = "LPF", metr = "temp_psnr")
    #do_learn(circ = "HPF", metr = "temp_psnr")
    #do_learn(circ = "DER", metr = "temp_psnr")
    #do_learn(circ = "SWI", metr = "beats")
    #do_learn(circ = "all", metr = "beats")


# %%
