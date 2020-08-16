CityConst={}
def checkCity(str):
  return str in CityConst
def getCityCode(str):
  return CityConst[str]
def addCityCode(str,val):
  CityConst[str]=val
def showConst():
  return CityConst
