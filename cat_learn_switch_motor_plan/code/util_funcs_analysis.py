from imports import *


def power_func(x, a, b, c):
    res = a * x**b + c
    return res


def tanh_func(x, a, b, c):
    res = a * np.tanh(b * (x - 1)) + c
    return res


def fit_func(d, dv, func):
    x = d['trial_abs'].to_numpy()
    y = d[dv].to_numpy()
    ppopt, pcov = curve_fit(func, x, y, maxfev=1e5, bounds=(0, 1))
    acc_pred = func(x, *ppopt)
    _, _, r, _, _ = linregress(y, acc_pred)
    r2 = r**2
    # plt.plot(x, y)
    # plt.plot(x, func(x, *ppopt))
    # plt.show()
    d['fit_a'] = ppopt[0]
    d['fit_b'] = ppopt[1]
    d['fit_c'] = ppopt[2]
    d['fit_ac'] = ppopt[0] + ppopt[2]
    d[dv + '_pred'] = acc_pred
    d['r2'] = r2
    return d


def inspect_tanh():
    # NOTE: tanh_func parameters
    # asymtote = a + c
    # rate = b
    # initial accuracy = c

    a = [0.1, 0.4]
    b = [1]
    c = [0.1, 0.35]
    x = np.arange(1, 24, 1)
    for aa in a:
        for bb in b:
            for cc in c:
                lab = 'a= ' + str(aa) + ', b= ' + str(bb) + ', c= ' + str(cc)
                # plt.plot(x, aa * x**bb + cc, label=lab)
                plt.plot(x, aa * np.tanh(bb * (x - 1)) + cc, label=lab)
                plt.legend()
    plt.show()


def fit_dbm(d, model_func, side, k, model_name):

    n = d.shape[0]

    fit_args = {
        'obj_func': None,
        'bounds': None,
        'disp': False,
        'maxiter': 3000,
        'popsize': 20,
        'mutation': 0.7,
        'recombination': 0.5,
        'tol': 1e-5,
        'polish': False,
        'updating': 'deferred',
        'workers': 1
    }

    obj_func = fit_args['obj_func']
    bounds = fit_args['bounds']
    maxiter = fit_args['maxiter']
    disp = fit_args['disp']
    tol = fit_args['tol']
    polish = fit_args['polish']
    updating = fit_args['updating']
    workers = fit_args['workers']
    popsize = fit_args['popsize']
    mutation = fit_args['mutation']
    recombination = fit_args['recombination']

    drec = []
    for m, mod in enumerate(model_func):

        dd = d

        cat = dd.cat.to_numpy()
        x = dd.x.to_numpy()
        y = dd.y.to_numpy()
        resp = dd.resp.to_numpy()

        cat = cat - 1
        resp = resp - 1

        # rescale x and y to be [0, 100]
        range_x = np.max(x) - np.min(x)
        x = ((x - np.min(x)) / range_x) * 100
        range_y = np.max(y) - np.min(y)
        y = ((y - np.min(y)) / range_y) * 100

        # compute glc bnds
        yub = np.max(y) + 0.1 * range_y
        ylb = np.min(y) - 0.1 * range_y
        bub = 2 * np.max([yub, -ylb])
        blb = -bub
        nlb = 0.001
        nub = np.max([range_x, range_y]) / 2

        if 'unix' in model_name[m]:
            bnd = ((0, 100), (nlb, nub))
        elif 'uniy' in model_name[m]:
            bnd = ((0, 100), (nlb, nub))
        elif 'glc' in model_name[m]:
            bnd = ((-1, 1), (blb, bub), (nlb, nub))
        elif 'gcc' in model_name[m]:
            bnd = ((0, 100), (0, 100), (nlb, nub))

        z_limit = 3

        args = (z_limit, cat, x, y, resp, side[m])

        if model_name[m] == 'nll_guess':
            nll = nll_guess(args)
            results = {'x': [-1], 'fun': nll}

        elif model_name[m] == 'nll_biased_guess':
            p, nll = nll_biased_guess(args)
            results = {'x': [p], 'fun': nll}

        else:
            results = differential_evolution(func=mod,
                                             bounds=bnd,
                                             args=args,
                                             disp=disp,
                                             maxiter=maxiter,
                                             popsize=popsize,
                                             mutation=mutation,
                                             recombination=recombination,
                                             tol=tol,
                                             polish=polish,
                                             updating=updating,
                                             workers=workers)

        tmp = np.concatenate((results['x'], [results['fun']]))
        tmp = np.reshape(tmp, (tmp.shape[0], 1))

        tmp = pd.DataFrame(results['x'])
        tmp.columns = ['p']
        tmp['nll'] = results['fun']
        tmp['bic'] = k[m] * np.log(n) + 2 * results['fun']
        # tmp['aic'] = k[m] * 2 + 2 * results['fun']
        tmp['model'] = model_name[m]
        drec.append(tmp)

    drec = pd.concat(drec)
    return drec


def plot_dbm(dbm, ax_title, ax):

    for s in dbm['participant'].unique():

        x = dbm.loc[dbm['participant'] == s]

        best_model = x['best_model'].to_numpy()[0]

        if best_model in ('nll_unix_0', 'nll_unix_1'):
            xc = x['p'].to_numpy()[0]
            ax.plot([xc, xc], [0, 100], 'C0', label='unix')

        elif best_model in ('nll_uniy_0', 'nll_uniy_1'):
            yc = x['p'].to_numpy()[0]
            ax.plot([0, 100], [yc, yc], 'C1', label='uniy')

        if best_model in ('nll_glc_0', 'nll_glc_1'):
            # a1 = results['x'][0]
            # a2 = np.sqrt(1 - a1**2)
            # b = results['x'][1]
            # print(x['p'])
            a1 = x['p'].to_numpy()[0]
            a2 = np.sqrt(1 - a1**2)
            b = x['p'].to_numpy()[1]
            ax.plot([0, 100], [-b / a2, -(100 * a1 + b) / a2],
                    'C2',
                    label='glc')

        elif best_model in ('nll_gcc_eq_0', 'nll_gcc_3'):
            xc = x['p'].to_numpy()[0]
            yc = x['p'].to_numpy()[1]
            ax.plot([0, xc], [yc, yc], '-k')
            ax.plot([xc, xc], [0, yc], '-k')

        ax.set_xlim(-5, 105)
        ax.set_ylim(-5, 105)
        ax.set_title(ax_title)


def nll_guess(args):
    '''
    - returns the negative loglikelihood of the guessing model
    - params format: []
    - args format: same as others
    '''

    z_limit = args[0]
    cat = args[1]
    x = args[2]
    y = args[3]
    resp = args[4]
    side = args[5]
    n = x.shape[0]

    nll = -n * np.log(0.5)

    return nll


def nll_biased_guess(args):
    '''
    - returns the negative loglikelihood of the biased guessing model
    - params format:  [] --- bias estimated directly from the data
    - z_limit is the z-score value beyond which one should truncate
    - data columns:  [cat x y resp]
    '''

    z_limit = args[0]
    cat = args[1]
    x = args[2]
    y = args[3]
    resp = args[4]
    side = args[5]

    n = x.shape[0]
    A_indices = np.where(resp == 0)[0]
    B_indices = np.where(resp == 1)[0]
    n_A = A_indices.shape[0]
    n_B = B_indices.shape[0]
    p_A = n / n_A if n_A > 0 else 0
    p_B = n / n_B if n_B > 0 else 0

    # TODO: is this right?
    nll_1 = -n_A * np.log(p_A) - n_B * np.log(p_B)
    nll_2 = -n_B * np.log(p_B) - n_A * np.log(p_A)
    nll = np.min([nll_1, nll_2])

    return p_A, nll


def nll_unix(params, *args):
    '''
    - returns the negative loglikelihood of the unidimensional X bound fit
    - params format:  [bias noise] (so x=bias is boundary)
    - z_limit is the z-score value beyond which one should truncate
    - data columns:  [cat x y resp]
    '''

    xc = params[0]
    noise = params[1]

    z_limit = args[0]
    cat = args[1]
    x = args[2]
    y = args[3]
    resp = args[4]
    side = args[5]

    n = x.shape[0]
    A_indices = np.where(resp == 0)
    B_indices = np.where(resp == 1)

    zscoresX = (x - xc) / noise
    zscoresX = np.clip(zscoresX, -z_limit, z_limit)

    if side == 0:
        prA = norm.cdf(zscoresX, 0.0, 1.0)
        prB = 1 - prA
    else:
        prB = norm.cdf(zscoresX, 0.0, 1.0)
        prA = 1 - prB

    log_A_probs = np.log(prA[A_indices])
    log_B_probs = np.log(prB[B_indices])

    nll = -(np.sum(log_A_probs) + sum(log_B_probs))

    return nll


def nll_uniy(params, *args):
    '''
    - returns the negative loglikelihood of the unidimensional Y bound fit
    - params format:  [bias noise] (so y=bias is boundary)
    - z_limit is the z-score value beyond which one should truncate
    - data columns:  [cat x y resp]
    '''

    yc = params[0]
    noise = params[1]

    z_limit = args[0]
    cat = args[1]
    x = args[2]
    y = args[3]
    resp = args[4]
    side = args[5]

    n = x.shape[0]
    A_indices = np.where(resp == 0)
    B_indices = np.where(resp == 1)

    zscoresY = (y - yc) / noise
    zscoresY = np.clip(zscoresY, -z_limit, z_limit)

    if side == 0:
        prA = norm.cdf(zscoresY, 0.0, 1.0)
        prB = 1 - prA
    else:
        prB = norm.cdf(zscoresY, 0.0, 1.0)
        prA = 1 - prB

    log_A_probs = np.log(prA[A_indices])
    log_B_probs = np.log(prB[B_indices])

    nll = -(np.sum(log_A_probs) + sum(log_B_probs))

    return nll


def nll_glc(params, *args):
    '''
    - returns the negative loglikelihood of the GLC
    - params format: [a1 b noise]
    -- a1*x+a2*y+b=0 is the linear bound
    -- assumes without loss of generality that:
    --- a2=sqrt(1-a1^2)
    --- a2 >= 0
    - z_limit is the z-score value beyond which one should truncate
    - data columns:  [cat x y resp]
    '''

    a1 = params[0]
    a2 = np.sqrt(1 - params[0]**2)
    b = params[1]
    noise = params[2]

    z_limit = args[0]
    cat = args[1]
    x = args[2]
    y = args[3]
    resp = args[4]
    side = args[5]

    n = x.shape[0]
    A_indices = np.where(resp == 0)
    B_indices = np.where(resp == 1)

    z_coefs = np.array([[a1, a2, b]]).T / params[2]
    data_info = np.array([x, y, np.ones(np.shape(x))]).T
    zscores = np.dot(data_info, z_coefs)
    zscores = np.clip(zscores, -z_limit, z_limit)

    if side == 0:
        prA = norm.cdf(zscores)
        prB = 1 - prA
    else:
        prB = norm.cdf(zscores)
        prA = 1 - prB

    log_A_probs = np.log(prA[A_indices])
    log_B_probs = np.log(prB[B_indices])

    nll = -(np.sum(log_A_probs) + np.sum(log_B_probs))

    return nll


def nll_gcc_eq(params, *args):
    '''
    returns the negative loglikelihood of the 2d data for the General
    Conjunctive Classifier with equal variance in the two dimensions.

    Parameters:
    params format: [biasX biasY noise] (so x = biasX and
    y = biasY make boundary)
    data row format:  [subject_response x y correct_response]
    z_limit is the z-score value beyond which one should truncate
    '''

    xc = params[0]
    yc = params[1]
    noise = params[2]

    z_limit = args[0]
    cat = args[1]
    x = args[2]
    y = args[3]
    resp = args[4]
    side = args[5]

    n = x.shape[0]
    A_indices = np.where(resp == 0)
    B_indices = np.where(resp == 1)

    if side == 0:
        zscoresX = (x - xc) / noise
        zscoresY = (y - yc) / noise
    if side == 1:
        zscoresX = (xc - x) / noise
        zscoresY = (y - yc) / noise
    if side == 2:
        zscoresX = (x - xc) / noise
        zscoresY = (yc - y) / noise
    else:
        zscoresX = (xc - x) / noise
        zscoresY = (yc - y) / noise

    zscoresX = np.clip(zscoresX, -z_limit, z_limit)
    zscoresY = np.clip(zscoresY, -z_limit, z_limit)

    pXB = norm.cdf(zscoresX)
    pYB = norm.cdf(zscoresY)

    prB = pXB * pYB
    prA = 1 - prB

    log_A_probs = np.log(prA[A_indices])
    log_B_probs = np.log(prB[B_indices])

    nll = -(np.sum(log_A_probs) + np.sum(log_B_probs))

    return nll


def val_gcc_eq(params, *args):
    '''
    Generates model responses for 2d data for the General Conjunctive
    Classifier with equal variance in the two dimensions.

    Parameters:
    params format: [biasX biasY noise] (so x = biasX and
    y = biasY make boundary)
    data row format:  [subject_response x y correct_response]
    z_limit is the z-score value beyond which one should truncate
    '''

    xc = params[0]
    yc = params[1]
    noise = params[2]

    z_limit = args[0]
    cat = args[1]
    x = args[2]
    y = args[3]
    resp = args[4]
    side = args[5]

    n = x.shape[0]
    A_indices = np.where(resp == 0)
    B_indices = np.where(resp == 1)

    if side == 0:
        zscoresX = (x - xc) / noise
        zscoresY = (y - yc) / noise
    if side == 1:
        zscoresX = (xc - x) / noise
        zscoresY = (y - yc) / noise
    if side == 2:
        zscoresX = (x - xc) / noise
        zscoresY = (yc - y) / noise
    else:
        zscoresX = (xc - x) / noise
        zscoresY = (yc - y) / noise

    zscoresX = np.clip(zscoresX, -z_limit, z_limit)
    zscoresY = np.clip(zscoresY, -z_limit, z_limit)

    pXB = norm.cdf(zscoresX)
    pYB = norm.cdf(zscoresY)

    prB = pXB * pYB
    prA = 1 - prB

    resp = np.random.uniform(size=prB.shape) < prB
    resp = resp.astype(int)

    return cat, x, y, resp


def val_glc(params, *args):
    '''
    Generates model responses for 2d data in the GLC.
    - params format: [a1 b noise]
    -- a1*x+a2*y+b=0 is the linear bound
    -- assumes without loss of generality that:
    --- a2=sqrt(1-a1^2)
    --- a2 >= 0
    - z_limit is the z-score value beyond which one should truncate
    - data columns:  [cat x y resp]
    '''

    a1 = params[0]
    a2 = np.sqrt(1 - params[0]**2)
    b = params[1]
    noise = params[2]

    z_limit = args[0]
    cat = args[1]
    x = args[2]
    y = args[3]
    resp = args[4]
    side = args[5]

    n = x.shape[0]
    A_indices = np.where(resp == 0)
    B_indices = np.where(resp == 1)

    z_coefs = np.array([[a1, a2, b]]).T / params[2]
    data_info = np.array([x, y, np.ones(np.shape(x))]).T
    zscores = np.dot(data_info, z_coefs)
    zscores = np.clip(zscores, -z_limit, z_limit)

    if side == 0:
        prA = norm.cdf(zscores)
        prB = 1 - prA
    else:
        prB = norm.cdf(zscores)
        prA = 1 - prB

    resp = np.random.uniform(size=prB.shape) < prB
    resp = resp.astype(int)

    return cat, x, y, resp