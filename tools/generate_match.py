#!/usr/bin/env python3
"""Original, deterministic fictional 80-second 11v11 match simulation.
No player, match, tracking coordinate or event is copied from an existing game.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'public' / 'data'
FPS = 5
DURATION = 80
PITCH = {'length_m': 105, 'width_m': 68}

# IDs, names and positions invented for this personal hackathon simulation.
HOME = [
 ('H1',1,'Rowan','GK',4,34), ('H2',2,'Blake','RB',25,14),
 ('H3',3,'Finch','LB',24,54), ('H4',4,'Quinn','CB',19,26),
 ('H5',5,'Rivera','CB',18,42), ('H6',6,'Hart','DM',32,31),
 ('H7',7,'Morgan','RW',58,12), ('H8',8,'Imani','CM',43,30),
 ('H9',9,'Taylor','ST',65,32), ('H10',10,'Ellis','AM',54,24),
 ('H11',11,'Nico','LW',56,55)]
AWAY = [
 ('A1',1,'Cole','GK',102,34), ('A2',2,'Kim','LB',83,12),
 ('A3',3,'Stone','RB',83,55), ('A4',4,'Reid','CB',88,40),
 ('A5',5,'Shah','CB',87,26), ('A6',6,'Park','DM',72,29),
 ('A7',7,'Foster','RW',55,55), ('A8',8,'Jules','CM',64,42),
 ('A9',9,'Lane','ST',52,31), ('A10',10,'Beck','AM',64,26),
 ('A11',11,'Ash','LW',56,13)]

# Focus players have bespoke positional keyframes; all others have conservative drift.
KEYS = {
 'H6': [(0,32,31),(9,39,31),(20,45,33),(40,49,33),(80,47,34)],
 'H8': [(0,43,30),(10.2,49,29),(18,55,27),(28,60,30),(55,68,34),(80,63,32)],
 'H10':[(0,54,24),(19.3,62,25),(34,70,25),(43,73,25),(60,80,29),(80,78,31)],
 'H7': [(0,58,12),(25,67,11),(43,76,12),(53,84,19),(56,86,21),(80,80,21)],
 'H9': [(0,65,32),(30,77,33),(43,82,34),(51,89,32),(56,94,31),(61,98,32),(80,95,33)],
 'A1': [(0,102,34),(60,102,34),(62,103,33),(67,102,34),(80,102,34)],
 'A4': [(0,88,40),(25,87,40),(43,88,40),(62,92,42),(68.7,93,43),(76,88,43),(80,82,43)],
 'A5': [(0,87,26),(35,88,28),(56,94,26),(65,97,28),(80,94,30)],
 'A2': [(0,83,12),(40,86,15),(57,91,21),(80,89,25)],
 'A6': [(0,72,29),(25,71,28),(35,72,26),(43,75,26),(56,82,27),(80,72,29)],
}

players = []
for team, roster in [('home',HOME),('away',AWAY)]:
    for pid, number, name, role, x, y in roster:
        players.append({'id':pid,'team_id':team,'number':number,'name':name,'role':role})
        if pid not in KEYS:
            sign = 1 if team == 'home' else -1
            offset = 0 if role == 'GK' else sign * (2.2 if role in ['CB','RB','LB'] else 4.2)
            KEYS[pid] = [(0,x,y),(25,x+offset*0.45,y+(0.5 if number%2 else -0.5)),
                         (50,x+offset,y),(80,x+offset*0.5,y)]

PLAYER_BY_ID = {x['id']:x for x in players}


def position(player_id, t):
    keys = KEYS[player_id]
    if t <= keys[0][0]:
        return keys[0][1], keys[0][2]
    for (t1,x1,y1),(t2,x2,y2) in zip(keys,keys[1:]):
        if t <= t2:
            f = (t-t1)/(t2-t1)
            # smooth interpolation between original keypoints (velocity never extreme)
            return x1+(x2-x1)*f, y1+(y2-y1)*f
    return keys[-1][1], keys[-1][2]

# Each motion segment has a plausible touch owner and one point-to-point ball flight.
PASSAGES = [
    (9.0,10.2,'H6','H8'),
    (18.0,19.3,'H8','H10'),
    (43.0,44.5,'H10','H7'),
    (56.0,57.4,'H7','H9'),
    (61.0,61.6,'H9','A1'),
    (67.0,68.7,'A1','A4'),
    (76.0,77.2,'A4',None),
]


def ball_state(t):
    # Source player is aligned at launch time; target at receipt time.
    for start,end,src,dst in PASSAGES:
        if start <= t < end:
            f = (t-start)/(end-start)
            a = position(src,start)
            b = position(dst,end) if dst else (74,43)
            return (a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f, None)
    if t < 9: return (*position('H6',t),'H6')
    if t < 18: return (*position('H8',t),'H8')
    if t < 43: return (*position('H10',t),'H10')
    if t < 56: return (*position('H7',t),'H7')
    if t < 61: return (*position('H9',t),'H9')
    if t < 67: return (*position('A1',t),'A1')
    if t < 76: return (*position('A4',t),'A4')
    return (74,43,None)

# Narrations are authored, deterministic baseline content, NOT AI-generated.
# 'reason' is a testable explanation for humans; the cloud model can rewrite it.
EVENTS = [
  ('E00',0.0,'phase','home','H6',None,'in_play','Rivergate build in midfield.',
   'Rivergate have the ball in their own half and are beginning an attacking move.',
   'The attack starts with safe possession before the first forward pass.',1),
  ('E01',9.0,'pass','home','H6','H8','complete','Hart passes to Imani.',
   'Hart moves the ball forward to Imani, Rivergate number eight in midfield.',
   'The pass advances the ball into central midfield without surrendering possession.',2),
  ('E02',18.0,'pass','home','H8','H10','complete','Imani finds Ellis.',
   'Imani picks out Ellis between midfield and the attacking line.',
   'Ellis receives further upfield, creating a new forward passing option.',2),
  ('E03',27.0,'carry','home','H10',None,'in_play','Ellis drives forward.',
   'Ellis carries the ball across midfield toward the edge of the final third.',
   'Holding possession while moving forward draws defenders toward the ball.',1),
  ('E04',35.0,'pressure','away','A6','H10','applied','Park closes down Ellis.',
   'Northbridge midfielder Park moves close to Ellis. Ellis still has possession.',
   'A nearby defender gives Ellis less time on the ball; pressure is not the same as a turnover.',2),
  ('E05',43.0,'pass','home','H10','H7','complete','Ellis passes right to Morgan.',
   'Ellis spots Morgan wide on the right and sends the ball across to the winger.',
   'The switch moves play away from the defender applying central pressure.',3),
  ('E06',51.0,'run','home','H9',None,'off_ball','Taylor moves behind the defence.',
   'While Morgan has the ball, Taylor makes a forward run towards the penalty area.',
   'The run gives Morgan a forward passing target closer to goal.',2),
  ('E07',56.0,'pass','home','H7','H9','complete','Morgan plays Taylor through.',
   'Morgan slips the ball inside to Taylor, now close to the penalty area.',
   'The pass connects the wide player to the runner in a threatening area.',3),
  ('E08',61.0,'shot','home','H9',None,'on_target','Taylor shoots!',
   'Taylor takes a shot from inside the penalty area. The ball is travelling towards Cole.',
   'A shot on target creates a direct chance, but there is no confirmed goal.',4),
  ('E09',62.0,'save','away','A1','H9','saved','Cole makes the save.',
   'Northbridge goalkeeper Cole stops the shot and takes control of the ball.',
   'The save ends the Rivergate attack without a goal.',4),
  ('E10',67.0,'pass','away','A1','A4','complete','Cole finds Reid.',
   'Cole releases the ball to defender Reid as Northbridge begin to play out.',
   'Northbridge retain possession after the save and begin their own phase.',1),
  ('E11',76.0,'clearance','away','A4',None,'in_play','Reid clears into midfield.',
   'Reid sends the ball upfield, away from the Northbridge penalty area.',
   'The clearance moves the ball away from immediate danger; the next possession is not established.',1),
]

frames = []
for i in range(FPS*DURATION+1):
    ms = round(i*1000/FPS)
    t = ms/1000
    bx,by,owner = ball_state(t)
    pr = PLAYER_BY_ID[owner] if owner else None
    frames.append({'t_ms':ms,
                   'ball':{'x':round(bx,2),'y':round(by,2)},
                   'possession':({'team_id':pr['team_id'],'player_id':owner} if owner else None),
                   'players':[{'id':p['id'],'x':round(position(p['id'],t)[0],2),'y':round(position(p['id'],t)[1],2)} for p in players]})

events=[]
for event_id,t,kind,team_id,pid,target,outcome,essential,detailed,why,priority in EVENTS:
    x,y = position(pid,t)
    nearest = []
    for q in players:
        if q['team_id']!=PLAYER_BY_ID[pid]['team_id']:
            qx,qy=position(q['id'],t)
            nearest.append((math.hypot(x-qx,y-qy),q['id']))
    d,opp_id=min(nearest)
    # Completion and on-target status are unavailable until the receiving / shot frame.
    # Round up to a sample frame so the asserted evidence exists at the stated time.
    flight = next(((start, end, dst) for start,end,src,dst in PASSAGES
                   if abs(start-t)<0.0001 and src==pid), None)
    if kind in ('pass','shot'):
        assert flight is not None, f'No ball flight for confirmed {kind}: {event_id}'
        end=flight[1]
        resolved_ms=int(math.ceil(end * FPS - 1e-9) * 1000 / FPS)
    else:
        resolved_ms=round(t*1000)
    endpos=position(target,flight[1]) if target and kind=='pass' else None
    forward_m=round(endpos[0]-x,1) if endpos else None
    observed_ms=round(t*1000)
    events.append({'id':event_id,'t_ms':observed_ms,'observed_at_ms':observed_ms,
                   'resolved_at_ms':resolved_ms,'available_at_ms':resolved_ms,'kind':kind,
                   'team_id':team_id,'player_id':pid,'recipient_id':target,
                   'outcome':outcome,'priority':priority,
                   'location_m':{'x':round(x,2),'y':round(y,2)},
                   'facts':{'nearest_opponent_id':opp_id,'nearest_opponent_distance_m':round(d,1),
                            'forward_progress_m':forward_m,'confirmed_goal':False},
                   'narration':{'essential':essential,'detailed':detailed},
                   'why':why,
                   'evidence':{'frame_t_ms':resolved_ms,'observation_frame_t_ms':observed_ms,
                               'source':'original synthetic frames and authored events'}})

match = {
  'schema_version':'0.2',
  'match_id':'FWB-SYNTH-001',
  'synthetic':True,
  'provenance':'Original fictional test fixture; not a reconstruction of any real match or dataset.',
  'title':'An attack everyone can follow',
  'duration_ms':DURATION*1000,
  'fps':FPS,
  'pitch':{'length_m':105,'width_m':68,
           'coordinate_system':'metres; top-left=(0,0), bottom-right=(105,68); home attacks to increasing X'},
  'teams':[{'id':'home','name':'Rivergate','short':'RIV','attacks':'right','kit':'yellow circle'},
           {'id':'away','name':'Northbridge','short':'NOR','attacks':'left','kit':'cyan square'}],
  'players':players,'events':events,'frames':frames,
  'result':{'home_goals':0,'away_goals':0,'is_full_match':False},
  'important_notes':['A synthetic passage rather than a real match',
                     'Frame positions are made-up and internally interpolated',
                     'Initial narration is deterministic; cloud model integration is optional',
                     'No goal is scored']
}

OUTPUT.mkdir(parents=True,exist_ok=True)
text=json.dumps(match,separators=(',',':'),ensure_ascii=False)
(OUTPUT/'match.json').write_text(json.dumps(match,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(OUTPUT/'match.js').write_text('/* Generated deterministic fixture: see tools/generate_match.py */\nwindow.FWB_MATCH = '+text+';\n',encoding='utf-8')
print(f"Generated {DURATION}s at {FPS}Hz: {len(frames)} frames, {len(players)} players, {len(events)} events, {len(text)} compact bytes")
