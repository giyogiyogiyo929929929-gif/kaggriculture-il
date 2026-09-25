

# ---- v131 candidate: one-unit next-turn pure-cash SELL preemption ----
# Parent: exact v115_champion_same_turn_open_squeeze.py (SHA256 c6b9986f...).
# Single mechanism: when a non-funding-critical pure-cash SELL is scheduled next turn,
# move exactly one unit into a safe free market slot now and subtract exactly one unit
# from that item's returned SELL next turn. Route, total planned SELL quantity, BUY/HERD/
# FARM decisions, and every other order are unchanged.
_V131_SP_PARENT = agent
_V131_SP_ITEMS = ('STRAWBERRY','WOOL','EGG','MILK','MELON','CARROT','TOMATO')
_V131_SP_STATE = {}
_V131_SP_REPORT = {
    'calls':0,'fires':0,'repaid':0,'errors':0,'skips_slots':0,'skips_funding':0,
    'skips_town_draw':0,'skips_stock':0,'skips_clone':0,'last_event':None,
}

def _v131_sp_reset(player, step):
    st=_V131_SP_STATE.get(player)
    if st is None or step==0 or step < st.get('step', -1):
        st={'step':step,'debt':{}}
        _V131_SP_STATE[player]=st
    else:
        st['step']=step
    return st

def _v131_sp_repay(step, market, debt):
    changed=False
    for (due,item),n in list(debt.items()):
        if due!=step or n<=0:continue
        left=n
        for o in market:
            if left<=0:break
            if not o or len(o)<3 or o[0]!='SELL' or o[1]!=item:continue
            try:q=max(0,int(o[2]))
            except Exception:continue
            cut=min(q,left)
            if cut:
                o[2]=q-cut;left-=cut;changed=True;_V131_SP_REPORT['repaid']+=cut
        if left<=0:debt.pop((due,item),None)
        else:debt[(due,item)]=left
    return changed

def _v131_sp_future_sale(obs):
    step=int(obs['step']); player=int(obs['player']); due=step+1
    if due>718:return None
    try:orders=[list(o) for o in (_adv_future(player,due) or [])]
    except Exception:return None
    # Protect the first market order if it is a SELL: inherited EXP293 treats this
    # position as potentially funding-critical for the following turn.
    protected_item = orders[0][1] if orders and len(orders[0])>=2 and orders[0][0]=='SELL' else None
    for idx,o in enumerate(orders):
        if not o or len(o)<3 or o[0]!='SELL' or o[1] not in _V131_SP_ITEMS:continue
        item=o[1]
        try:q=max(0,int(o[2]))
        except Exception:continue
        if q<2:continue
        if idx==0 or item==protected_item:
            _V131_SP_REPORT['skips_funding']+=1;continue
        return due,item,q,idx
    return None

def _v131_sp_apply(obs, action):
    step=int(obs['step']); player=int(obs['player']); st=_v131_sp_reset(player,step)
    market=[list(o) for o in (action.get('market') or [])]
    changed=_v131_sp_repay(step,market,st['debt'])
    # no new preempt at dawn boundary, terminal step, or on a full order list
    if step>=718 or step%24==23 or len(market)>=10:
        if len(market)>=10:_V131_SP_REPORT['skips_slots']+=1
        if changed:
            out=dict(action);out['market']=market;return out
        return action
    # Keep the mechanism on the mirror/clone family where a rival matching SELL
    # is a plausible lockstep counterparty; otherwise a one-turn move is speculative.
    try:clone=bool(_v44y_clone_gate(obs))
    except Exception:clone=False
    if not clone:
        _V131_SP_REPORT['skips_clone']+=1
        if changed:
            out=dict(action);out['market']=market;return out
        return action
    # Do not insert before an existing product-market transaction. This preserves the
    # current turn's product quote choreography and avoids changing BUY_PRODUCT funding.
    if any(o and len(o)>1 and o[0]=='BUY_PRODUCT' for o in market):
        if changed:
            out=dict(action);out['market']=market;return out
        return action
    target=_v131_sp_future_sale(obs)
    if target is None:
        if changed:
            out=dict(action);out['market']=market;return out
        return action
    due,item,orig_q,orig_idx=target
    # If town will consume this product between now and the original SELL, moving it
    # earlier can forfeit a deterministic recovery in quote; abstain.
    try:
        shops=list((obs.get('town') or {}).get('unlocked_shops',[]))
        draw=_v9_town_draw(shops,step)
        if int(draw.get(item,0))>0:
            _V131_SP_REPORT['skips_town_draw']+=1
            if changed:
                out=dict(action);out['market']=market;return out
            return action
    except Exception:
        pass
    # Require one genuinely available unit after the parent action and after current
    # SELL commitments. Never borrow from a pickup in progress.
    stock=projected_shed(action,FarmView(obs))
    current_selling=0
    for o in market:
        if o and len(o)>=3 and o[0]=='SELL' and o[1]==item:
            try:current_selling+=max(0,int(o[2]))
            except Exception:pass
    avail=max(0,int(stock.get(item,0))-current_selling)
    if avail<1:
        _V131_SP_REPORT['skips_stock']+=1
        if changed:
            out=dict(action);out['market']=market;return out
        return action
    # Split exactly one unit into the current turn. Append at the final free slot so
    # all inherited current-turn order precedence is preserved.
    market.append(['SELL',item,1])
    st['debt'][(due,item)]=st['debt'].get((due,item),0)+1
    _V131_SP_REPORT['fires']+=1
    inv=int((obs.get('market') or {}).get('inventory',{}).get(item,0))
    price=int((obs.get('market') or {}).get('prices',{}).get(item,0))
    rival=obs['farms'][1-player]
    animal={'EGG':'GOOSE','MILK':'COW','WOOL':'SHEEP'}.get(item)
    crop=item if item in ('CARROT','TOMATO','STRAWBERRY','MELON') else None
    standing=sum(max(0,int(t.get('yield_units',0))) for row in rival.get('tiles',[]) for t in row
                 if isinstance(t,dict) and ((crop and t.get('crop')==crop) or (animal and t.get('animal')==animal)))
    edge=0.0
    try:
        # Counterfactual proxy: value of selling one unit before an 8+ visible-rival batch.
        params={k:dict(v) for k,v in _R37_MARKET_PARAMS.items()}
        for k,p in (obs.get('market') or {}).get('params',{}).items():
            if k in params:params[k].update(p)
        batch=min(24,max(8,standing))
        edge=float(_r37_market_price(item,inv,params)-_r37_market_price(item,inv+batch,params))
    except Exception:pass
    _V131_SP_REPORT['last_event']={
        'step':step,'product':item,'original_sell_step':due,'new_sell_step':step,
        'original_quantity':orig_q,'split_quantity':1,'market_inventory':inv,
        'own_inventory':int(stock.get(item,0)),'rival_visible_yield':standing,
        'quoted_price':price,'estimated_counterfactual_relative_edge':edge,
        'gate_reason':'clone,next_turn_nonfirst_sell,no_town_draw,free_slot,stock_available',
    }
    out=dict(action);out['market']=market;return out

def agent(observation,configuration=None):
    if int(observation.get('step',0))==0:
        for k in list(_V131_SP_REPORT):
            if k=='last_event':_V131_SP_REPORT[k]=None
            elif isinstance(_V131_SP_REPORT[k],(int,float)):_V131_SP_REPORT[k]=0
    _V131_SP_REPORT['calls']+=1
    action=_V131_SP_PARENT(observation,configuration)
    try:return _v131_sp_apply(observation,action)
    except Exception:
        _V131_SP_REPORT['errors']+=1
        return action
agent.telemetry=_V131_SP_REPORT
kaggle_submission_agent_v131_purecash_sell1_preempt=agent
