from difflib import SequenceMatcher
import config as cfg
from selenium.webdriver.common.by import By
import difflib

def getAttributes(d, e):
   obj={}
   try:
      if e is None:
            return None
      attributes = d.execute_script("""
            var items = {}; 
            for (index = 0; index < arguments[0].attributes.length; ++index) {
                 items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value
            }; 
            return items;
       """, e)
      t=e.get_attribute("value")
      if t is not None:
         obj['text'] =t
      t=e.get_attribute('innerText')
      if t is not None:
         obj['innertext'] = t
      obj['tag'] = e.tag_name
      obj['attrs'] = attributes
      #print("attributes extracted:", obj)
      return obj
   except Exception as ex:
      print(f"Exception in getAttributes: {ex}")
      return None

def string_similarity(s1, s2):
    """Return similarity ratio between 0 and 1."""
    if not s1 or not s2:
        return 0
    return SequenceMatcher(None, s1, s2).ratio()

def tag_similarity(oldElement, newElement):
   old_tag=oldElement.get("tag", "").lower()
   old_type=oldElement['attrs'].get("type", "").lower()

   if old_tag=='input' and old_type=='':
      old_type='text'
   new_tag=newElement.get("tag", "").lower()
   new_type = newElement['attrs'].get("type", "").lower()

   if new_tag=='input' and new_type=='':
      new_type='text'
   #text controls
   if old_tag=='input' and old_type=='text' and new_tag=='textarea':
      return True
   if old_tag=='textarea' and new_tag=='input' and new_type=='text':
      return True

   #button
   if old_tag in ['input','button'] and old_type in ['submit','button'] and new_tag in ['a','button','img'] and new_type in ['submit','button','']:
      return True
   if new_tag in ['input', 'button'] and new_type in ['submit', 'button'] and old_tag in ['a', 'button','img'] and old_type in ['submit', 'button', '']:
      return True

   #link & image
   if old_tag in ['a','img'] and new_tag in ['a','img','button'] and new_type in ['submit', 'button', '']:
      return True
   if new_tag in ['a', 'img'] and old_tag in ['a', 'img', 'button'] and old_type in ['submit', 'button', '']:
      return True
   return False


def compare_element_texts(oldElement, newElement):
   text1 = oldElement.get('text','') or oldElement.get('innertext','')
   text2 = newElement.get('text','') or newElement.get('innertext','')
   similarity = difflib.SequenceMatcher(None, str(text1).strip(), str(text2).strip()).ratio()*.10
   return similarity

def getElementScore(failedElement,newElement, mainelement=True):
      print('getElementScore failedElement', failedElement)
      print('getElementScore newElement', newElement)

      score=0
      tag_score=0
      key_attrscore=0
      nonkey_attrscore=0
      text_score=0

      mx_keyattr=0
      mx_nonkeyattr=0

      for attributeKey in failedElement['attrs'].keys():
          if attributeKey.lower() !="xpath":
              if attributeKey.lower() in ['id', 'name', 'class_name', 'css_selector', 'for']:
                  mx_keyattr+=1
              else:
                  mx_nonkeyattr+=1



      #maxAttrs = len(list(failedElement['attrs'].keys()))
      #if 'xpath' in failedElement['attrs'].keys():
      #   maxAttrs -= 1
      maxAttrs=mx_keyattr+mx_nonkeyattr
      print('maxattrs', maxAttrs)
      try:
         if failedElement.get("tag", "")==newElement.get("tag",""):
            tag_score =.15
            print(failedElement.get("tag", ""), newElement.get("tag",""))
         elif tag_similarity(failedElement, newElement):
            tag_score =.1
            print(tag_similarity(failedElement, newElement))
      except:
         pass
      print("tag match", tag_score)

      #print('score after tag/tag_sim/text_sim',score)
      try:
         if maxAttrs>0:
             for attributeKey in failedElement['attrs'].keys():
                 if attributeKey.lower()!='xpath':
                    oldElementAttr = failedElement['attrs'].get(attributeKey, "")
                    newElementAttr =  newElement['attrs'].get(attributeKey, "")
                    #print("Test Attribute", attributeKey, oldElementAttr, newElementAttr, maxAttrs)
                    if attributeKey.lower() in ['id', 'name', 'class_name', 'css_selector', 'for']:
                        key_attrscore +=(difflib.SequenceMatcher(None, oldElementAttr, newElementAttr).ratio()*(.75/mx_keyattr))
                    else:
                        nonkey_attrscore += (difflib.SequenceMatcher(None, oldElementAttr, newElementAttr).ratio() * (.25 / mx_nonkeyattr))
                #print('attrs',score)

             #print('score after attrs', score)
         else:
             if maxAttrs==len(list(newElement['attrs'].keys())):
                key_attrscore =.75
                nonkey_attrscore=0
             else:
                key_attrscore =0
                nonkey_attrscore=0

      except:
            pass

      if mainelement:
        if key_attrscore >= .75:
            key_attrscore += .1

      print("attr match", key_attrscore, nonkey_attrscore)

      #text score
      try:
         text_score= compare_element_texts(failedElement,  newElement)
      except:
            pass

      print("txt match", text_score)

      score=(tag_score+key_attrscore+nonkey_attrscore+text_score)

      print("tag_score", tag_score)
      print("key_attrscore", key_attrscore)
      print("nonkey_attrscore", nonkey_attrscore)
      print("text_score", text_score)


      print("final score", score)

      return tag_score,key_attrscore,nonkey_attrscore,text_score, score



def check_element_exists_in_or(newElement):
    for key in cfg.or_data.keys():
        old_attrs = cfg.or_data[key]['attrs'].copy()  # avoid modifying original
        old_attrs["xpath"] = ""
        new_attrs = newElement['attrs'].copy()
        new_attrs["xpath"] = ""

        if old_attrs == new_attrs and \
           cfg.or_data[key]['text'] == newElement['text'] and \
           cfg.or_data[key]['innertext'] == newElement['innertext'] and \
           cfg.or_data[key]['tag'] == newElement['tag']:
            return True  # found a match

    return False  # no match found after checking all elements


def selfHealEngine(driver, failedElement):
   best_match = None
   best_score = 0
   best_attrs = None
   scoreType=None
   best_key_attr_score = 0
   best_self_score = 0
   best_context_score = 0

   elements = driver.find_elements(By.XPATH, "//*")
   for element in elements:
    score = 0
    selfScore = 0
    parentScore = 0
    preSiblingScore = 0
    folSiblingScore = 0
    contextScore = 0
    tag_score = 0
    key_attrscore= 0
    nonkey_attrscore= 0
    text_score= 0

    attributes = getAttributes(driver, element)
    em=check_element_exists_in_or(attributes)
    if not em:

        print('old element 1', failedElement)
        print('new element 1', attributes)
        print(em)

        print('self score')
        #self score
        try:
         tag_score,key_attrscore,nonkey_attrscore,text_score, selfScore = getElementScore(failedElement,attributes, True)
        except Exception as e:
            print(f"Exception in selfHealEngine while calculating selfScore: {e}")
            selfScore=0
        print('Self Score:', selfScore)

        print('context score')
        #context score

        try:
            parent_attributes=getAttributes(driver, element.find_element(By.XPATH, ".."))
            _,_,_,_, parentScore=getElementScore(failedElement['parent'],parent_attributes, False)
            parentScore=parentScore*.40
        except:
            pass

        print('Parent Score:', parentScore)

        try:
            preSibling_attributes=getAttributes(driver, element.find_element(By.XPATH, "preceding-sibling::*[1]"))
            _,_,_,_, preSiblingScore=getElementScore(failedElement['pre_sibling'],preSibling_attributes, False)
            preSiblingScore=preSiblingScore*.25
        except:
            pass
        print('Pre Sibling Score:', preSiblingScore)

        try:
            folSibling_attributes=getAttributes(driver, element.find_element(By.XPATH, "following-sibling::*[1]"))
            _,_,_,_, folSiblingScore=getElementScore(failedElement['fol_sibling'],folSibling_attributes, False)
            folSiblingScore=folSiblingScore*.15
        except:
            pass
        print('fol Sibling Score:', folSiblingScore)

        contextScore=(parentScore+preSiblingScore+folSiblingScore)
        if contextScore>=.8:
            contextScore+=.15
        print('Context Score:', contextScore)

        score=selfScore+contextScore
        print('Total Score:', score)
        print("key_attrscore", key_attrscore)
        print("best_key_attr_score", best_key_attr_score)

        if score > best_score or ( key_attrscore > best_key_attr_score and contextScore>=.8):
                best_key_attr_score=key_attrscore
                best_score = score
                best_match = element
                best_attrs = attributes
                #print('Test:', best_score, best_attrs)
                scoreType=cfg.get_element_confidence_score(best_score)

   if scoreType in cfg.ELEMENT_HEALING_THRESHOLD and best_match:
       print('final:', best_score, best_attrs,scoreType)
       return best_score, best_match, best_attrs,scoreType
   else:
       #print("No suitable match found with the given threshold.")
       return 0, None, None,None





