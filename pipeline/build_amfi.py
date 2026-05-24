import requests, re, json
H={"User-Agent":"Mozilla/5.0"}
r=requests.get("https://www.amfiindia.com/spages/NAVAll.txt",headers=H,timeout=60)
open("NAVAll.txt","w").write(r.text)
schemes=[]
cur_amc=None
for line in r.text.split("\n"):
    line=line.rstrip()
    if not line: continue
    if ";" not in line:
        # AMC header line
        if line.strip() and "Mutual Fund" in line: cur_amc=line.strip()
        continue
    parts=line.split(";")
    if len(parts)>=6 and parts[0].strip().isdigit():
        code=parts[0].strip(); isin1=parts[1].strip(); isin2=parts[2].strip()
        name=parts[3].strip(); nav=parts[4].strip(); date=parts[5].strip()
        try: nav=float(nav)
        except: nav=None
        schemes.append({"code":code,"isin1":isin1,"isin2":isin2,"name":name,"nav":nav,"date":date,"amc":cur_amc})
print("total schemes:",len(schemes))
print("with NAV:",sum(1 for s in schemes if s["nav"]))
# AMCs
amcs=set(s["amc"] for s in schemes if s["amc"])
print("AMCs:",len(amcs))
json.dump(schemes,open("amfi_schemes.json","w"))
# sample
for s in schemes[:3]: print(" ",s["code"],s["name"][:50],s["nav"],"|",s["amc"])
