import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as chrome_options
from selenium.webdriver.edge.options import Options as edge_options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
import os
#
import config as cfg
import SelfHealingEngine as she
import filemanager as fm


class webui:
    driver = None
    driverOptions = None
    action = None

    def runstep(self, tname, stepname, stepdef):
        print("running")
        action = stepdef["action"]
        try:

            if action.lower() in ["loadpage", "openwebpage"]:
                status, err=self.openwebpage(stepdef)
            elif action.lower() in ["settext", "setvalue"]:
                status, err=self.settext(stepdef)
            elif action.lower() in ["click"]:
                status, err=self.click(stepdef)
            elif action.lower() in ["smartwait"]:
                status, err=self.smartwait(stepdef)
            elif action.lower() in ["selectdropdown"]:
                status, err=self.selectdropdown(stepdef)
            elif action.lower() in ["selectradiogroup"]:
                status, err=self.selectradiogroup(stepdef)
            elif action.lower() in ["selectcheckbox"]:
                status, err=self.selectcheckbox(stepdef)
            elif action.lower() in ["alert"]:
                status, err=self.selectalert(stepdef)
            elif action.lower() in ["selectframe"]:
                status, err=self.selectframe(stepdef)
            elif action.lower() in ["switchtoparent"]:
                status, err=self.switchtoparent(stepdef)
            elif action.lower() in ["switchtowindow"]:
                status, err=self.switchtowindow(stepdef)
            elif action.lower() in ["uploadfiles"]:
                status, err=self.uploadfiles(stepdef)
            elif action.lower() in ["close", "quit", "closebrowser", "quitbrowser"]:
                status, err=self.closebrowser()
            else:
                print(tname, "action not found:", action)
                status=False
                err=f"{action} not found"

            return status, err
        except Exception as e:
            print("Error", action, stepdef, e)
            return False, e


    def getelement(self, objdesc):
        obj=[]
        locators = {}
        index = 0
        or_desc=None
        objname=None
        try:
            if isinstance(objdesc, str):
                objname= objdesc
                or_desc = cfg.or_data[objname]

                for key in or_desc.keys():
                    if key!='attrs':
                        locators[key]=or_desc[key]

                for key in or_desc['attrs'].keys():
                    locators[key] = or_desc['attrs'][key]
                #objRepoUsed=True
            #elif isinstance(objdesc, dict):
                #or_desc = objdesc
            print("Locators for", objname, ":", locators)
            for key in locators.keys():
                tmpobj=None
                by = key
                value = locators[key]
                print(objname, by, value)
                if by == "id":
                    tmpobj= self.driver.find_elements(By.ID, value)
                elif by == "name":
                    tmpobj= self.driver.find_elements(By.NAME, value)
                elif by == "class":
                    tmpobj= self.driver.find_elements(By.CLASS_NAME, value)
                elif by == "tag_name":#???
                    tmpobj= self.driver.find_elements(By.TAG_NAME, value)
                elif by == "partial_link_text":#???
                    tmpobj= self.driver.find_elements(By.PARTIAL_LINK_TEXT, value)
                elif by == "css":
                    tmpobj= self.driver.find_elements(By.CSS_SELECTOR, value)
                elif by == "xpath":
                    tmpobj= self.driver.find_elements(By.XPATH, value)
                elif by == "index":
                    index=int(value)

                if tmpobj is not None:
                    if by in ["id", "name", "class", "tag", "text", "css", "xpath"] and len(tmpobj)>0:
                        if obj==[]:
                            obj=tmpobj
                        else:
                            obj = list(set(obj) & set(tmpobj))



            if obj is None:
                obj=[]

            print("Elements found:", len(obj))

            for o in obj:
                print("Element:", she.getAttributes(self.driver, o))

            if len(obj)==0:
                # webelement not found!!!
                print("self-healing needed for", objname)
                oldElement = cfg.or_data[objname]

                score, newElement, newElementAttributes, score_type = she.selfHealEngine(self.driver, oldElement)
                print("ne", newElementAttributes)
                if newElement is not None:
                    # webObj= getElement(newObjDesc)
                    webelement = newElement
                    print("Element healed:")
                    print("old element", oldElement)
                    print("new element", newElementAttributes)
                    print("score", score)
                    print("score type", score_type)

                    webelementproperties = she.getAttributes(self.driver, webelement)
                    try:
                        parentelementprops = webelement.find_element(By.XPATH, "..")
                        webelementproperties['parent'] = she.getAttributes(self.driver, parentelementprops)
                    except:
                        webelementproperties['parent'] = None

                    try:
                        precidingsiblingprops = webelement.find_element(By.XPATH, "preceding-sibling::*[1]")
                        webelementproperties['precedingsibling'] = she.getAttributes(self.driver, precidingsiblingprops)
                    except:
                        webelementproperties['precedingsibling'] = None

                    try:
                        followingsiblingprops = webelement.find_element(By.XPATH, "following-sibling::*[1]")
                        webelementproperties['followingsibling'] = she.getAttributes(self.driver, followingsiblingprops)
                    except:
                        webelementproperties['followingsibling'] = None

                    if cfg.or_data[objname] != webelementproperties:
                        cfg.or_data[objname] = webelementproperties
                        if cfg.UPDATE_OR_ON_HEAL:
                            fm.saveor()

                    self.elementmanager(webelement)
                    return webelement, ""
                else:
                    print("Element could not be healed:", objname)
                    return None, "Element not found and could not be healed"

            else:
                #webelement found!!!!
                if index == -1:
                    index = len(obj) - 1
                    webelement = obj[-1]
                elif len(obj) == 1:
                    webelement = obj[0]
                elif len(obj) > 0 and index >= 0 and index < len(obj):
                    webelement = obj[index]
                else:
                    webelement = obj[-1]

            if objname is not None and cfg.UPDATE_OR_ON_NEW_DESC_FOUND:
                # get parent & siblings to describe better
                webelementproperties = she.getAttributes(self.driver, webelement)
                try:
                    parentelementprops = webelement.find_element(By.XPATH, "..")
                    webelementproperties['parent'] = she.getAttributes(self.driver, parentelementprops)
                except:
                    webelementproperties['parent'] = None

                try:
                    precidingsiblingprops = webelement.find_element(By.XPATH, "preceding-sibling::*[1]")
                    webelementproperties['precedingsibling'] = she.getAttributes(self.driver, precidingsiblingprops)
                except:
                    webelementproperties['precedingsibling'] = None

                try:
                    followingsiblingprops = webelement.find_element(By.XPATH, "following-sibling::*[1]")
                    webelementproperties['followingsibling'] = she.getAttributes(self.driver, followingsiblingprops)
                except:
                    webelementproperties['followingsibling'] = None

                if cfg.or_data[objname] != webelementproperties:
                    cfg.or_data[objname] = webelementproperties
                    fm.saveor()


            ###
            self.elementmanager(webelement)
            return webelement, ""
        except Exception as e:
            print("Error in getElement:", e)
            return None, e

    def elementmanager(self, webelement):
        #make sure element is visible
        try:
            WebDriverWait(self.driver, 20).until(ec.visibility_of_element_located(webelement))
        except:
            pass

        #make sure element is clickable
        try:
            WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable(webelement))
        except:
            pass

        #move to element
        try:
            self.action.move_to_element(webelement)
        except:
            pass

        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", webelement)
        except:
            pass

        #highligh element
        try:
            if cfg.ELEMENT_HIGHLIGHT:
                org_style = webelement.get_attribute("style")
                for _ in range (cfg.ELEMENT_HIGHLIGHT_BLINK):
                    self.driver.execute_script(
                        f"arguments[0].style.border='{cfg.ELEMENT_HIGHLIGHT_SIZE}px solid "
                        f"{cfg.ELEMENT_HIGHLIGHT_COLOR}'", webelement)
                    time.sleep(.3)
                    self.driver.execute_script("arguments[0].style.border='none'", webelement)
                    self.driver.execute_script("arguments[0].setAttribute('style', arguments[1])", webelement, org_style)
                    time.sleep(.3)
        except:
            pass














    def openwebpage(self, stepdef):
        try:
            browser = stepdef["params"].get("browser", "chrome")
            url = stepdef["params"].get("url", "about:blank")
            wait = int(stepdef.get("wait", 2))
            browser_options = stepdef["params"].get("options", [])
            experimental_options = stepdef["params"].get("experimentalOptions", [])
            driver_options_flag=False
            if browser.lower() == "chrome":
                self.driverOptions = chrome_options()
            else:
                self.driverOptions = edge_options()

            if browser_options is not None and browser_options != []:
                driver_options_flag=True
                for option in browser_options:
                    self.driverOptions.add_argument(option)

            if experimental_options is not None and experimental_options != []:
                if browser_options is None or browser_options == []:
                    driver_options_flag = True
                for option in experimental_options:
                    try:
                        self.driverOptions.add_experimental_option(option['key'], option['value'])
                    except:
                        pass


            if browser.lower() == "chrome":
                if driver_options_flag:
                    self.driver = webdriver.Chrome(self.driverOptions)
                else:
                    self.driver = webdriver.Chrome()
            elif browser.lower() == "edge":
                if driver_options_flag:
                    self.driver = webdriver.Edge(self.driverOptions)
                else:
                    self.driver = webdriver.Edge()

            cfg.action = ActionChains(self.driver)
            self.driver.get(url)
            time.sleep(wait)
            return True, ""
        except Exception as e:
            return False, e


    def smartwait(self, o):
        try:
            obj = o['params']['objectname']
            exitwhenfound = o['params'].get('exitwhenfound', False)

            while True:
                time.sleep(2)
                o = self.getelement(obj)
                # o=cfg.driver.find_elements(By.XPATH, obj)
                # print(len(o))
                if exitwhenfound:
                    if o:
                        break
                else:
                    if not o:
                        break
            return True, ""
        except Exception as e:
            return False, e

    def getdatadict(self, dd):
        id=dd.get("id", "*")
        colname=dd.get("col", "")
        if id=="*":
            id=random.choice(list(cfg.data_dict.keys()))

        if len(colname.strip())>0:
            return cfg.data_dict[id].get(colname, "")
        else:
            return ""

    #set text
    def settext(self, obj):
        try:
            print("set text called", obj)
            webobject=obj['params']["objectname"]
            text=obj['params'].get("value", "")
            print("set text called1", text)

            if isinstance(text, dict):
                text=self.getdatadict(text)

            print("set text called2", text)
            if isinstance(text, list):
                text=random.choice(text)

            keys=obj['params'].get("keys", [])
            wait = int(obj.get("wait", 2))
            repeat=int(obj.get("repeat", 1))

            print("set text called2.1")
            webelement, err = self.getelement(webobject)
            print("set text called2.2")
            print(err)
            if webelement is None:
                return False, err

            for i in range(repeat):
                print("set text called3", text)
                webelement.clear()
                if len(keys)>0:
                    print("set text called4", text)
                    self.sendkeys(webelement, keys)
                else:
                    print("set text called5", text)
                    webelement.send_keys(text)
                time.sleep(wait)

            return True, ""
        except Exception as e:
            return False, e

    #send keys
    def sendkeys(self, obj, keys):
        m=[]
        for k in keys:
            if k in cfg.KEY_MAP.keys():
                if k == 'ctrl' and cfg.osName=='MAC':
                    k="cmd"

                m.append(cfg.KEY_MAP.get(k))
            else:
                m.append(k)
        obj.send_keys(*m)

    #click
    def click(self, obj):
        try:
            webobject=obj['params']["objectname"]
            wait = int(obj.get("wait", 2))
            repeat=int(obj.get("repeat", 1))
            webelement, err = self.getelement(webobject)

            if webelement is None:
                return False, err

            for i in range(repeat):
                webelement.click()
                time.sleep(wait)

            return True, ""
        except Exception as e:
            print('Error in click', e)
            return False, e

    #select from dropdown
    def selectdropdown(self, obj):
        try:
            webobject=obj['params']["objectname"]
            selectby=obj['params']["objectname"]
            value = obj['params']["value"]
            wait = int(obj.get("wait", 2))
            repeat=int(obj.get("repeat", 1))

            webelement, err = self.getelement(webobject)
            if webelement is None:
                return False, err

            select = Select(webelement)

            for i in range(repeat):
                if selectby.lower()=="value":
                    select.select_by_value(value)
                elif selectby.lower()=="text":
                    select.select_by_visible_text(value)
                elif selectby.lower()=="index":
                    select.select_by_index(int(value))

            time.sleep(wait)
            return True, ""
        except Exception as e:
            print('Error in selectDropdown', e)
            return False, e

    #chgeck checkbox
    def selectcheckbox(self, obj):
        try:
            webobject=obj['params']["objectname"]
            check = obj['params']["value"]
            wait = int(obj.get("wait", 2))
            repeat=int(obj.get("repeat", 1))

            webelement, err = self.getelement(webobject)

            if webelement is None:
                return False, err

            is_checked = webobject.is_selected()
            if check and not is_checked:
                webelement.click()
            elif not check and is_checked:
                webelement.click()
            time.sleep(wait)
            return True, ""
        except Exception as e:
            print('Error in checkCheckbox', e)
            return False, e

    #select radio
    def selectradiobutton(self, obj):
        try:
            webobject=obj['params']["objectname"]
            wait = int(obj.get("wait", 2))
            repeat=int(obj.get("repeat", 1))

            webelement, err = self.getelement(webobject)
            if webelement is None:
                return False, err

            webelement.click()
            time.sleep(wait)
            return True, ""
        except Exception as e:
            print('Error in selectRadioButton', e)
            return False, e


    #select radio group
    def selectradiogroup(self, obj):
        try:
            webobject=obj['params']["objectname"]
            wait = int(obj.get("wait", 2))
            value = obj['params']["value"]
            repeat=int(obj.get("repeat", 1))

            webelement,err = self.getelement(webobject)
            if webelement is None:
                return False, err

            radio_buttons = self.driver.find_elements(By.NAME, webelement.get_attribute("name"))
            for rb in radio_buttons:
                if rb.get_attribute("value") == value:
                    rb.click()
                    break
            time.sleep(wait)
            return True, ""
        except Exception as e:
            print('Error in selectRadioGroup', e)
            return False, ""


    #select frame
    def selectframe(self, obj):
        try:
            frame=obj['params']["frame"]
            wait = int(obj.get("wait", 2))

            self.driver.switch_to.frame(frame)
            time.sleep(wait)
            return True, ""
        except Exception as e:
            print('Error in selectFrame', e)
            return False, e


    #handle alert
    def selectalert(self, obj):
        try:
            accept_alert=obj['params']["acceptalert"]
            wait = int(obj.get("wait", 2))

            alert = self.driver.switch_to.alert

            if accept_alert:
                alert.accept()
            else:
                alert.dismiss()
            time.sleep(wait)
            return True, ""
        except Exception as e:
            print('Error in selectAlert', e)
            return False, e


    #switch back to parent window
    def switchtoparent(self, obj):
        try:
            wait = int(obj.get("wait", 2))

            self.driver.switch_to.default_content()
            time.sleep(wait)
            return True, ""
        except Exception as e:
            print('Error in switchTpParent', e)
            return False, e


    #switch to window
    def switchtowindow(self, obj):
        try:
            wait = int(obj.get("wait", 2))
            window_id=obj.get("windowid", None)
            window_name = str(obj.get("windowname", "")).lower()
            switched=False
            WebDriverWait(self.driver, wait).until(lambda d: len(d.window_handles) > 1)
            current_handle = self.driver.current_window_handle

            if len(self.driver.window_handles) > 1:
                if window_id:
                    if 0 <= int(window_id) < len(self.driver.window_handles):
                        self.driver.switch_to.window(self.driver.window_handles[window_id])
                        switched = True
                elif window_name:
                    for handle in self.driver.window_handles:
                        self.driver.switch_to.window(handle)
                        if window_name in self.driver.title.lower():
                            switched= True
                            break

                if not switched:
                    self.driver.switch_to.window(current_handle)
            return True, ""
        except Exception as e:
            print('Error in switchTpParent', e)
            return False, e

    def uploadfiles(self, obj):
        try:
            # Extract all params from obj
            webobject = obj['params']["objectname"]
            file_paths = obj['params']["file_paths"]
            wait = int(obj.get("wait", 2))
            repeat = int(obj.get("repeat", 1))

            webelement, err = self.getelement(webobject)
            if webelement is None:
                return False, err

            files_to_upload="\n".join(file_paths)
            webelement.send_keys(files_to_upload)

            time.sleep(wait)

            return True, ""
        except Exception as e:
            print("Upload failed:", e)
            return False, e


    def takescreenshot(self, v):
        filename = v['params'].get('filename', 'screenshot')
        outputpath = v['params'].get('outputpath', 'C:\\Users\\byrajsw\\Documents\\ChatMFC\screenshots')

        # Normalize path
        outputpath = os.path.normpath(outputpath)
        print(outputpath)
        if not os.path.exists(outputpath):
            os.makedirs(outputpath)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(outputpath, f"{filename}_{timestamp}.png")

        print(f"Saving screenshot to: {filepath}")
        success = self.driver.save_screenshot(filepath)

        if success:
            print(f"Screenshot saved successfully at: {filepath}")
        else:
            print("Screenshot failed!")

            #close browser
    def closebrowser(self):
        try:
            self.driver.quit()
            return True, ""
        except Exception as e:
            return False, e


