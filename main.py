# -*- coding: utf8 -*-

import json
import re
from ulti import remove_accents
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
#Install python-Levenshtein for faster runtime

#hiện tại em đưa lần lượt 1 bài từ data.json vào file sample.json rồi test
with open('sample.json') as f:
    sample = json.load(f)


#pattern to capture numbers
numeric_const_pattern = ' (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] \d+ ) ?'
rx = re.compile(numeric_const_pattern, re.VERBOSE)
#pattern to capture AxB
r2 = re.compile(r'\d+[.,]?\d*\s?(m2|m)?\s?[xX*]\s?\d+[.,]?\d*', re.VERBOSE)

"""deal with dt cong nhan"""
def deal_with_dt_congnhan(sample, key_dt_congnhan):
  area_cal = 0
  calculation = 1
  info_of_areacal = []
  hecta = ["ha", "hecta"]
  in_hecta = False #the area is in hecta rather than meter square

#iterate through the content, if an area item follows a normal one, we investigate further
  for item in range(len(sample["attributes"]) - 1):

    if sample["attributes"][item]["type"]=="area" and sample["attributes"][item-1]["type"] == "normal":
      #clean up the content of normal item and area item: remove accents,space and replace comma with dot
      format_areacontent = re.sub(r'\s+', '', sample["attributes"][item]["content"])
      format_areacontent = format_areacontent.replace(',','.')

      format_normalcontent = re.sub(r'\s+', '', sample["attributes"][item-1]["content"])

      areacontent = remove_accents(format_areacontent)
      normalcontent = remove_accents(format_normalcontent)
      #check hecta
      if hecta[0] in areacontent or hecta[1] in areacontent:
        in_hecta = True
      #fuzzy matching normal content with our list of keywords, since dt_congnhan is unique and of highest priority, only take in when requirements are met
      highest_ratio = process.extractOne(normalcontent,key_dt_congnhan)
      #if match ratio is high we take in the numbers
      if highest_ratio[1] >= 80:
        a_x_b = r2.search(areacontent) #take in numbers in format a x b
        if a_x_b != None:
          info_of_areacal = rx.findall(a_x_b.group()) 
        else:
          info_of_areacal = rx.findall(areacontent) #if the numbers are not in format a x b then we take in all available numbers

        info_of_areacal = [float(i) for i in info_of_areacal] #convert all to float
  
  #base on how many numbers we take in, assign area_cal accordingly
  if len(info_of_areacal) == 1:
    area_cal = info_of_areacal[0] 
  elif len(info_of_areacal) == 2:
    if info_of_areacal[0] > 2 and info_of_areacal[1] > 2: #numbers are written as "dai x m rong y m"
      area_cal = info_of_areacal[0]*info_of_areacal[1]
    elif info_of_areacal[0] > 2 and info_of_areacal[1] == 2: #numbers are written as "x m2"
      area_cal = info_of_areacal[0]
  elif len(info_of_areacal) > 2: #numbers are written as "dt a x b = c "
    for i in range(2):
        calculation *= info_of_areacal[i]
    area_cal = calculation
  #check hecta
  if in_hecta == True:
    area_cal *= 10000

  if area_cal != 0:
    return area_cal
  else:
    return 0


"""deal with dt dat"""
def deal_with_dt_dat(sample, key_dt_dat, special_case):
  area_cal = 0
  calculation = 1
  info_of_areacal = []
  hecta = ["ha", "hecta"]
  in_hecta = False
  array_of_area = []
  array_of_price = []
  
  for item in range(len(sample["attributes"]) - 1):

    if sample["attributes"][item]["type"]=="area":
      calculation = 1
      #clean up the content of prev item and area item: remove accents,space and replace comma with dot
      format_areacontent = re.sub(r'\s+', '', sample["attributes"][item]["content"])
      format_areacontent = format_areacontent.replace(',','.')

      format_prevcontent = re.sub(r'\s+', '', sample["attributes"][item-1]["content"])

      areacontent = remove_accents(format_areacontent)
      prevcontent = remove_accents(format_prevcontent)
      #check hecta
      if hecta[0] in areacontent or hecta[1] in areacontent:
        in_hecta = True
      #fuzzy matching for keywords in prevcontent and the appearance of "m2" or "ha" in area content
      highest_ratio = process.extractOne(prevcontent,key_dt_dat)
      ratio_of_m2 = fuzz.partial_ratio(areacontent,"m2")
      ratio_of_ha = fuzz.partial_ratio(areacontent,"ha")
      #req for dt is more vague so data only needs to met one of the condition to be taken in
      if highest_ratio[1] >= 60 and (ratio_of_m2 >= 50 or ratio_of_ha >= 80):
        a_x_b = r2.search(areacontent)
        if a_x_b != None:
          info_of_areacal = rx.findall(a_x_b.group())
        else:
          info_of_areacal = rx.findall(areacontent)
        info_of_areacal = [float(i) for i in info_of_areacal]

        #base on how many numbers we take in, assign area_cal accordingly
        if len(info_of_areacal) == 1:
          area_cal = info_of_areacal[0]
          array_of_area.append(area_cal) #append result to an array in case there are multiple ones
        elif len(info_of_areacal) == 2:
          if info_of_areacal[0] > 2 and info_of_areacal[1] > 2:
            area_cal = info_of_areacal[0]*info_of_areacal[1]
            array_of_area.append(area_cal)  #append result 
          elif info_of_areacal[0] > 2 and info_of_areacal[1] == 2:
            area_cal = info_of_areacal[0]
            array_of_area.append(area_cal) #append result 
        elif len(info_of_areacal) > 2: #numbers are written as "dt a x b = c" or it's a range " dt 300m2 - 500m2"
          for i in range(len(info_of_areacal)):
            if info_of_areacal[i] == 2:
              i += 1
            else:
              calculation *= info_of_areacal[i]
              area_cal = calculation
          array_of_area.append(area_cal) #append result 

  #print("array of area",array_of_area)

  #price array
  price_without_unit_list  = []
  for item in range(len(sample["attributes"]) - 1):
    if sample["attributes"][item]["type"]=="price":
      price_content = sample["attributes"][item]["content"]
      price_content = re.sub(r'\s+', '',price_content)
      price_content = price_content.replace(',','.')
      price_content = remove_accents(price_content)

      holder = rx.findall(price_content)
      for item in holder:
        price_without_unit_list.append(item)
      array_of_price.append(price_content)

  #print("array of price",array_of_price)

  #if there are 3 or more items in the array or 2 items and they are unique -> special case
  if len(array_of_area) == 2:
    if abs(array_of_area[1] - array_of_area[0] >= 30):
      special_case = True
  elif len(array_of_area) > 2:
    special_case = True

  #Choosing area with lowest price 
  if len(array_of_price) <= 2: #no prices to be found
    area_cal = max(array_of_area)
  else: #array of price exists
    price_in_ti = []
    price_in_trieu = []
    for item in array_of_price:
      ratio_of_ty = fuzz.partial_ratio(item,"ty")
      ratio_of_ti = fuzz.partial_ratio(item,"ty")
      if ratio_of_ti >= 80 or ratio_of_ty >= 80:
        price_in_ti.append(price_without_unit_list[array_of_price.index(item)])
      else:
        price_in_trieu.append(price_without_unit_list[array_of_price.index(item)])

    min_price_in_ti = min(price_in_ti)
    min_price_in_trieu = min(price_in_trieu)
    if min_price_in_trieu != 0:
      area_cal = array_of_area[price_without_unit_list.index(min_price_in_trieu)]
    else:
      area_cal = array_of_area[price_without_unit_list.index(min_price_in_ty)]

  if in_hecta == True:
    area_cal *= 10000

  if area_cal != 0:
    return area_cal, special_case
  else:
    return 0, special_case


"""deal with dt xaydung/san"""
def deal_with_dt_xaydung_san(sample, key_dt_xaydung_san):
  area_cal = 0
  calculation = 1
  info_of_areacal = [] 
  in_hecta = False

  for item in range(len(sample["attributes"]) - 1):

    if sample["attributes"][item]["type"] == "area":
      #clean up the content of prev item and area item: remove accents,space and replace comma with dot 
      format_areacontent = re.sub(r'\s+', '', sample["attributes"][item]["content"])
      format_areacontent = format_areacontent.replace(',','.')
      
      format_prevcontent = re.sub(r'\s+', '', sample["attributes"][item-1]["content"])

      areacontent = remove_accents(format_areacontent)
      prevcontent = remove_accents(format_prevcontent)
      #fuzzy matching for keywords in prevcontent and the appearance of "m2" or "ha" in area content
      highest_ratio = process.extractOne(prevcontent,key_dt_xaydung_san)
      #if req is met then take in data
      if highest_ratio[1] >= 80:
        a_x_b = r2.search(areacontent)
        if a_x_b != None:
          info_of_areacal = rx.findall(a_x_b.group())
        else:
          info_of_areacal = rx.findall(areacontent)
        info_of_areacal = [float(i) for i in info_of_areacal]
  
  #base on how many numbers we take in, assign area_cal accordingly
  if len(info_of_areacal) == 1:
    area_cal = info_of_areacal[0]
  elif len(info_of_areacal) == 2:
    if info_of_areacal[0] > 2 and info_of_areacal[1] > 2:
      area_cal = info_of_areacal[0]*info_of_areacal[1]
    elif info_of_areacal[0] > 2 and info_of_areacal[1] == 2:
      area_cal = info_of_areacal[0]
  elif len(info_of_areacal) > 2:
    for i in range(2):
        calculation *= info_of_areacal[i]
    area_cal = calculation

  if in_hecta == True:
    area_cal *= 10000
  #divide by floors and return or if no floor then return
  if area_cal != 0:
    if sample["floor"] != 0: 
      return area_cal/sample["floor"]
    else:
      return area_cal
  else:
    return 0


def xacdinh(dict_input: dict) -> float:
  """Hướng giải quyết vấn đề: tạo 3 function phụ cho 3 loại dt, luôn gọi dt_congnhan và dt_dat vì có thể cùng xuất hiện, chỉ gọi dt_xaydung_san khi 2 cái trên đều trả về 0"""
  
  """dt_congnhan > dt_dat > dt_xaydung_san"""
#keywords to indicate the area is the type of area we are looking for
  key_dt_congnhan = ["dientichcongnhan","cn","dtcn","congnhan","so"]
  key_dt_dat = ["dientichdat","dat"]
  key_dt_xaydung_san = ["dientichxaydung","dientichsan","san","xaydung","dt"]

#initialize 3 type of area
  dt_congnhan = 0.0
  dt_dat = 0.0
  dt_xaydung_san = 0.0

#final result to return
  area_cal = 0.0
#Special case of multiple areas being sold 
  special_case = False

  ## code goes here
#dt_congnhan and dt_dat can appear simultaneously so we calculate both and then choose accordingly
  dt_congnhan = deal_with_dt_congnhan(sample, key_dt_congnhan)
  dt_dat, special_case = deal_with_dt_dat(sample, key_dt_dat, special_case)

  #print("dt_congnhan: ", dt_congnhan)
  #print("dt_dat: ",dt_dat)
#if not special_case and we have dt_congnhan then dt_congnhan is final result
  if dt_congnhan != 0:
    area_cal = dt_congnhan
  elif dt_dat != 0: 
    #if special_case is true or we don't have dt_congnhan then dt_dat is final result
    area_cal = dt_dat
  else:
    #if we don't have dt_congnhan and dt_dat then dt_xaydung_san is final result
    dt_xaydung_san = deal_with_dt_xaydung_san(sample, key_dt_xaydung_san)
    area_cal = dt_xaydung_san
    #print("dt_xaydung_san: ", dt_xaydung_san)

  if special_case:
    area_cal = dt_dat
  print("Final result area_cal = ", area_cal)
  #print("Special case: ", special_case)
  """ Terminal output details:(uncomment all 7 print() to see):
  array of area (Dãy các diện tích) 
  array of price (Dãy giá các mảnh đất)
  dt_congnhan(Dien tich cong nhan)
  dt_dat(Dien tich dat)
  dt_xaydung_san(Dien tich xay dung) - this won't show if dt dat or cong nhan exists
  area_cal(giá trị cuối trả về của function xacdinh) 
  Special case(có phải là case đặc biệt bán nhiều mảnh đất/căn hộ 1 lúc)"""
  ############################
  ## Return
  ############################
  return area_cal

#uncomment next line to run
xacdinh(sample)