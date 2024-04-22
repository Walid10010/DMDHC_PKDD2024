

delete_set = set([])

def start_sigma(sigma,ind_to_name,name_to_d2Punkt,rho,beta):
    global delete_set
    delete_set = set([])
    neue_nachbarn = set([])
    sigma.nachbar  = set(sigma.nachbar)
    for nachbar in sigma.nachbar:
        d2Punkt = name_to_d2Punkt[ind_to_name[nachbar]]
        neue_nachbarn.update(disjunkt(sigma,d2Punkt,rho,beta,nachbar))

    chain_cluster(sigma,ind_to_name,name_to_d2Punkt,rho,beta,neue_nachbarn)
    return sigma




def chain_cluster(sigma,ind_to_name,name_to_d2Punkt,rho,beta,neue_nachbarn):
    global delete_set
    sigma.nachbar.update(neue_nachbarn)
    sigma.nachbar = sigma.nachbar.difference(delete_set)
    delete_set = set([])
    tmp_nachbarn = set([])
    if len(neue_nachbarn) > 0:
        for nachbar in neue_nachbarn:
            d2Punkt =  name_to_d2Punkt[ind_to_name[nachbar]]
            tmp_nachbarn.update(disjunkt(sigma, d2Punkt, rho, beta, nachbar))
        chain_cluster(sigma,ind_to_name,name_to_d2Punkt,rho,beta,tmp_nachbarn)








def disjunkt(sigma,nachbar,rho,beta,ind):
    #Hinweis : delete_set entfernt??
    disjunkt_list = [_ for _  in nachbar.nachbar if _ not in sigma.nachbar]
    dichte_abfall = len(nachbar.nachbar) - len(disjunkt_list) < rho * len(disjunkt_list)
    # vgl_avg = nachbar.avg_k_distanz * beta > sigma.avg_k_distanz
    vgl_avg = len(nachbar.nachbar)  < len(sigma.nachbar) * beta
    if (dichte_abfall or vgl_avg):
        delete_set.add(ind)
        return set([])
    else:
        return set(disjunkt_list)
