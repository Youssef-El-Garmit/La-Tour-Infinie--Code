import copy
import math
from tkinter import *
import random
from PIL import Image, ImageTk
from turtle import *
import os, sys, subprocess



def heal(creature):
    if creature.hp == creature.hpmax:
        theGame().addMessage("Le nombres de points de vie de " + creature.name + " est deja au max.")
        return None
    PointdeVieajouter = 3  ##ici on fait ensorte que si le nombre de points de vie de la creature qui utilise une potion et deja au max
    creature.hp = creature.hp + 3  ##alors la potion ne sera pas utiliser et si la potion lui rajoute plus de point de vie que son nombre de point de vie max
    if creature.hp > creature.hpmax:  ## alors on utilise la potion met on rajoute seulement le nombre de points necessaire pour arrivé a son nombre de point de
        PointdeVieajouter = PointdeVieajouter - (creature.hp - creature.hpmax)  ## vie max
        creature.hp = creature.hpmax
    theGame().addMessage("Le " + creature.name + " à gagné " + str(
        PointdeVieajouter) + " points de vie, son niveau de vie est maintenant de " + str(creature.hp) + ".")
    return True


def teleport(creature, item):
    theGame().floor.rm(theGame().floor.pos(creature))
    theGame().floor.put(random.choice(theGame().floor._rooms).randEmptyCoord(theGame().floor), creature)
    theGame().addMessage(creature.name + " s'est teleporté")
    return item


class Element():
    def __init__(self, name, abbrv=None, imageAss=None):
        self.name = name
        self.abbrv = abbrv if abbrv != None else name[0]
        self.imageAss = imageAss

    def __repr__(self):
        return self.abbrv

    def description(self):
        return "<" + self.name + ">"

    def meet(self, hero):
        raise NotImplementedError("Not implemented yet")


class Boutique(Element):
    ### On cree une clase Boutique pour pouvoir l'utilisé dans le jeux
    def __init__(self, name="Boutique", abbrv="€", imageAss=None):
        Element.__init__(self, name, abbrv, imageAss=None)
        self.boutiqueEquip = []
        self.choix = [Element("Acheter un équipement"), Element("Vendre un équipement")]
        self.imageAss = imageAss
        ## Pour ne pas modifier de methode et se faire du travail en plus, en va utiliser la methode "select" pour
        ## demander au hero ce qu'il veut choisir

    ## On modifie la methode meet pour que le hero lorsqu'il rencontre la boutique, puissent choisir entre acheter ou vendre
    ## un equipement en echange d'or
    def meet(self, hero):
        for k in theGame().equipments:  ### Ici avec cette boucle nous mettons dans la boutique, à la vente,
            for x in theGame().equipments[k]:  ### tout les equipement possible que nous avons ecrit dans equipment
                if x.name == "Or":  ## sauf l'or bien evidemment
                    continue
                self.boutiqueEquip.append(x)

        ChoixAV = theGame().select(self.choix, "Bienvenue dans la boutique ! Que voulez vous faire ?\n")
        if ChoixAV == self.choix[0]:
            if theGame().hero.Or == 0:
                return theGame().addMessage("Vous ne pouvez rien achetez, vous avez 0 Or.")

            ### On decide mnt que le prix d'un equipement est egale a son niveau,que l'on trouve grace à trouveNiveauEquip, plus 1
            choixhero = theGame().select(self.boutiqueEquip, "Que voulez vous achetez ?\n")
            if not isinstance(choixhero, Element):
                return None
            NivElem = theGame().TrouveNiveauEquip(choixhero)
            PrixElem = NivElem + 2
            if PrixElem <= hero.Or:
                hero._inventory.append(choixhero)  ###On rajoute l'equipment dans l'inventaire
                hero.Or = hero.Or - PrixElem  ###On enleve l'or du hero utilisé pour l'achat
                theGame().addMessage(
                    "Bravo vous venez d'acheter " + str(choixhero.name) + " pour " + str(PrixElem) + " Or.")
            else:
                return theGame().addMessage(
                    "Vous n'avez pas assez pour acheter cet équipement qui coûte " + str(PrixElem) + " Or.")

        if ChoixAV == self.choix[1]:
            if theGame().hero._inventory == []:
                return theGame().addMessage("Vous n'avez à rien vendre, votre inventaire est vide.")
            choixhero = theGame().select(hero._inventory, "Que voulez vous vendre ?\n")
            if not isinstance(choixhero, Element):
                return None
            NivElem = theGame().TrouveNiveauEquip(choixhero)
            if NivElem == None:  ###exception au cas ou l'element choissit n'est pas un equipement present dans les equipement de base (ex: cles pour coffre)
                return theGame().addMessage("Desolé nous n'achetons pas cet équipement.")
            PrixElem = NivElem + 1
            hero._inventory.remove(choixhero)  ###On enleve l'equipment de l'inventaire
            hero.Or = hero.Or + PrixElem  ###On rajoute l'or du hero gagner avec l'achat
            theGame().addMessage(
                "Bravo vous venez de vendre " + str(choixhero.name) + " pour " + str(PrixElem) + " Or.")


### On créer la classe Coffre comme heritiere de la classe élément pour que le coffre puisse être mis dans la map et utilisé car c'est un element
class Coffre(Element):

    def __init__(self, name="Coffre", abbrv="¤", imageAss=None):
        Element.__init__(self, name, abbrv, imageAss=None)
        self.items = None
        self.imageAss = imageAss

    def meet(self, hero):
        self.items = theGame().equipments
        ### on modifie ici meet pour que l'équipement contenu dans le coffre soit de niveau supérieur au niveau de la carte (game level x 2), si
        ### existant , d'ou la boucle qui cherche le plus grand niveau, le plus proche du niveau superieur à la carte
        nivEquip = 2 * theGame().level
        while self.items.get(nivEquip) == None:
            nivEquip = nivEquip - 1

        ### Maintenant on fait en sorte que lorsque le hero rencontre le coffre, cette methode meet faire le tour de l'inventaire pour voir
        ### s'il contient une clé du coffre fort, sinon en envoie un msg disant au hero qu'il doit trouver une clés pour ouvrir le coffre
        ### et obtenir l'equipment cacher dedans
        for i in hero._inventory:
            if i.name == "Clé":
                hero._inventory.remove(i)
                equipMystere = self.items.get(nivEquip)[0]
                hero.take(equipMystere)
                theGame().addMessage("Vous avez trouvé un " + equipMystere.name + " dans le coffre fort !")
                return True
        ### Si aucune cles n'est trouver dans l'inventaire en envoie un msg disant au hero qu'il doit trouver une clés pour ouvrir le coffre
        ### et obtenir l'equipment cacher dedans
        else:
            theGame().addMessage("Vous devez trouvez la clé pour ouvrir le coffre.")


class Escaliers(Element):
    ### Ici nous créons une classe escaliers heritière de la classe Elements, que nous allons utilisé plus tard dans la Map

    def __init__(self, name="Escaliers", abbrv="=", imageAss=None):
        Element.__init__(self, name, abbrv, imageAss=None)
        self.imageAss = imageAss

    ### Les esaliers seront representé comme un elements, que le joueur devra rencontrer (meet) pour pouvoir monter d'étage
    ### Une fois rencontrer on creer tout simplement un nouveau sol "buildFloor" et change le niveau de l'étage, en remettant a zero
    ### le compteur de creature tué (utilisé pour cacher les cles des coffres dans les monstres
    def meet(self, hero):
        theGame().level = theGame().level + 1
        theGame().AffichePiege = False
        theGame().hero.creatureTue = 0
        theGame().buildFloor()


class Pieges(Element):
    ### On creer la classe pieges pour les pieges qui ne sont rien d'autres que des elements car ne bouge pas, avec
    ### l'abbrv egale a un point pour qu'a la representation on ne fasse pas la difference entre le sol (ground) et ces pieges
    def __init__(self, degat=1, name="Pieges invisible", abbrv=".", imageAss=None):
        Element.__init__(self, name, abbrv, imageAss=None)
        self.degat = degat  ## Comme se sont des pieges invisible on va mettre de petit degats qui vont
        self.imageAss = imageAss  ## augmenter en même temp que les étages

    def meet(self, hero):
        self.degat = self.degat * theGame().level
        hero.hp = hero.hp - self.degat
        theGame().floor.rm(theGame().floor.pos(self))  ### Le piège ne fait effet qu'une seul fois ensuite il disparait
        theGame().addMessage(
            "Vous êtes tombé sur un " + str(self.name) + " et vous avez perdu " + str(self.degat) + " points de vie!!")


class Equipment(Element):

    def __init__(self, name, abbrv=None, usage=None, imageAss=None):
        Element.__init__(self, name, abbrv, imageAss=None)
        self.usage = usage
        self.imageAss = imageAss

    def meet(self, hero):
        Pris = hero.take(self)
        if Pris == True:
            theGame().addMessage("Vous avez pris " + str(self.name) + ".")
            return True

    def use(self, creature):
        try:
            if self.name == "Potion Vision":
                if not (isinstance(creature, Hero)):
                    theGame().addMessage(self.name + " n'est pas utilisable par le " + creature.name + ".")
                    return False
                else:
                    if theGame().AffichePiege == True:
                        theGame().addMessage("Le " + creature.name + " à utilisé " + self.name + ".")
                        theGame().addMessage(
                            "Or les Pièges étaient déja visibles, vous venez donc d'utiliser \nbêtement votre " + self.name + ".")
                        return True
                    theGame().AffichePiege = True
                    theGame().addMessage("Le " + creature.name + " à utilisé " + self.name + ".")
                    theGame().addMessage("Les Pièges sont devenus visibles.")
                    return True
            utilisable = self.usage(self, creature)
            if self.usage == None or utilisable == None:
                theGame().addMessage(self.name + " n'est pas utilisable par le " + creature.name + ".")
                return False
            theGame().addMessage("Le " + creature.name + " à utilisé " + self.name + ".")
            return utilisable
        except:
            theGame().addMessage(self.name + " n'est pas utilisable par le " + creature.name + ".")


class Armes(Equipment):
    ### Ici on creer la classe correspondant au armes qui est hereditaire de equipement car se sont des equipement
    def __init__(self, name, degat, abbrv="", ArmesJet=None, utilisationUnique=None, usage=None, imageAss=None):
        Equipment.__init__(self, name, abbrv, usage, imageAss=None)
        self.degat = degat
        ### Meme instance que Equipement qauf que l'on rajoute l'instance correspondant au degats infligés par cette armes
        self.ArmesJet = ArmesJet
        self.utilisationUnique = utilisationUnique
        self.imageAss = imageAss

    def use(self, hero):
        if isinstance(hero.ArmesEquiper, Armes):
            if isinstance(hero, Hero):
                hero.take(hero.ArmesEquiper)  ### ci une arme est deja equiper on remet cette derniere dans l'inventaire
            if isinstance(hero.ArmesEquiper,
                          Armes):  ##si c'est une armejet on rajoute pas les deagts a la force de heros car elle envoie des projectile
                if hero.ArmesEquiper == None:
                    hero.strength = hero.strength - hero.ArmesEquiper.degat  ### et on enleve les degat qu'elle avait rajouter a la force du hero
        ### Ceci permet donc de changer d'armes tout en les conservant dans l'inventaire

        hero.ArmesEquiper = self  ##Mnt on equipe le hero de la nouvelle arme
        if isinstance(hero, Hero):
            hero._inventory.remove(self)  ## et on l'enleve de l'equipement si c'est le hero qui l'utilise
        if hero.ArmesEquiper.ArmesJet == None:
            hero.strength = hero.strength + self.degat  ### on rajoute les degats a la force du joueur
        if self.ArmesJet == None and hero.name != "Sniper":
            theGame().addMessage(hero.name + " est equipé de " + self.name + " ( Dégâts : " + str(
                self.degat) + " ), sa puissance est maintenant de " + str(hero.strength) + ".")

        elif (isinstance(hero, Hero) or hero.name == "Sniper") and self.ArmesJet == True:
            theGame().addMessage(hero.name + " est equipé de " + self.name + " ( Dégâts : " + str(self.degat) + " ).")
            return True
        else:
            theGame().addMessage("Or " + self.name + " n'est pas utilisable par " + hero.name + ".")


class Creature(Element):
    def __init__(self, name, hp, abbrv=None, strength=1, imageAss=None):
        Element.__init__(self, name, abbrv, imageAss=None)
        self.hp = hp
        self.hpmax = hp
        self.strength = strength
        self.XPdonne = self.hp * 10
        ### On créer une instance correspondant au nombre d'XP que peut rapporter une creature si elle est tué, (utilisé dans XP)
        self.ArmesEquiper = "Aucune"  ##On creer une instance permettant de savoir de quel arme est equipé un monstre (pour jetequipement)
        self._inventory = []
        self.imageAss = imageAss

    def description(self):

        if isinstance(self, Hero):
            return Element.description(self) + "( Pts de vie : " + str(self.hp) + ", Force : " + str(
                self.strength) + ")"
        else:
            return Element.description(self) + "( Pts de vie : " + str(self.hp) + ", Force : " + str(
                self.strength) + ")"

    def meet(self, other, ArmeJet=None):
        if isinstance(self, Creature):
            ArmeUtiliser = theGame().hero.ArmesEquiper
            if ArmeJet == True:  ##on rajoute ce if dans la methode pour que si l'arme utilisé par le heros est une arme de jet (qui peut tirer de loin)
                ## on enleve a la creature toucher le nombre de degats de l'arme et non le nombre de degats du heros plus l'arme
                if ArmeUtiliser.utilisationUnique == None:
                    theGame().addMessage(str(other.name) + " tire avec " + ArmeUtiliser.name + " sur " + str(
                        self.description()) + " et lui enlève " + str(ArmeUtiliser.degat) + " points de vie.")
                if ArmeUtiliser.utilisationUnique != None:
                    theGame().addMessage(str(other.name) + " lance " + ArmeUtiliser.name + " sur " + str(
                        self.description()) + " et lui enleve " + str(
                        theGame().hero.ArmesEquiper.degat) + " points de vie.")
                self.hp = self.hp - theGame().hero.ArmesEquiper.degat
                if self.hp > 0:
                    return False
                self.hp = 0  ##juste pour l'esthetique pour que dans le message afficher cocernant les point de vie ne soit pas un chiffre negatif



            else:
                self.hp = self.hp - other.strength
                if self.hp <= 0:
                    self.hp = 0  ##juste pour l'esthetique pour que dans le message afficher cocernant les point de vie ne soit pas un chiffre negatif
                if other.name == "Sniper":
                    theGame().addMessage(
                        "Un projectile de " + str(other.description()) + " à touché le " + str(self.name) + ".")

                else:
                    if isinstance(other, Hero):
                        theGame().addMessage(str(other.name) + " frappe " + str(self.description()) + ".")
                    else:
                        theGame().addMessage(str(other.description()) + " frappe " + str(self.name) + ".")
                if self.hp > 0:
                    return False

        ### Nous avons modifié la methode "meet" pour lorsque le hero tue la creature qui cache la clés, cette derniere ce met directement dans l'inventaire du hero
        if isinstance(other, Hero):
            other.creatureTue = other.creatureTue + 1
            if other.creatureTue == theGame().floor.ClesTrouver:
                other.take(Equipment("Clé"))
                theGame().addMessage("Vous avez trouvé la clé en tuant le " + self.name + " !")
            ##on met egalement le fait que lorsque le heros tue un monstre le nombre d'xp que rapporte ce monstre lui soit directement mis dans ces Xp
            if self.hp <= 0 and isinstance(self, Creature):
                other.xp += self.XPdonne
                theGame().addMessage("Felicitation vous avez gagnez " + str(self.XPdonne) + "XP !")

        return True

    def JetPrincipal(self, direction, Archet=None, Nonutilisable=None):

        ## Ici cette methode va nous permettre de connaitre la pos max en enchainant une direction chosit,
        ## avant sortir de la map, ou sinon elle va nous donné la creature que rencontre cette element pour pouvoir l'utilisé dans Jetutilisation
        ## mais elle va aussi nous permettre de detecter lorsqu'elle est utilisé par l'archet (archet=True), lorsque le heros est dans la ligne de mire
        ## de l'archet ou lorsque l hero avec une arme est ce tir touche une creature ou non

        posHero = theGame().floor.pos(self)
        posEquipJeter = theGame().floor.pos(self)
        finMap = None

        try:
            while theGame().floor.get(posEquipJeter) == theGame().floor.ground or theGame().floor.get(
                    posEquipJeter) == self or isinstance(theGame().floor.get(posEquipJeter), Pieges):
                ###ici dans cette boucle nous regardons quel est la pos max ou peut allez l'element avant de rencontrer un autre element ou sortir
                posEquipJeter = posEquipJeter + direction  ###On met cette exception pour que si la direction anticipé sort de la map
                ### il n'y est pas d'erreur
        except:
            posEquipJeter = posEquipJeter - direction
            finMap = True

        if Archet == True and isinstance(theGame().floor.get(posEquipJeter), Hero) and theGame().floor.get(
                posEquipJeter).name != "Sniper":
            return True  ### ici ce if nous permet de verifier si la pos obtenu correspond au heros (pour l'archet)

        if Nonutilisable == None:  ##Si l'element envoye n'est pas utilisable par la creature toucher on saute se if pour deposer
            ## l'element devant la creature si possible
            if isinstance(theGame().floor.get(posEquipJeter), Creature) and not isinstance(
                    theGame().floor.get(posEquipJeter), Hero):
                ##if ArmesJet==True:    ##dans le cas ou on utilise cette methode pour une armes de tir (armesjet==True) si le tir
                ##return True  ## atteint une creature on renvoie True
                return theGame().floor.get(
                    posEquipJeter)  ###si la pos correspond a une creature (autre que le hero) elle renvoit la creature

        if finMap == None:
            posEquipJeter = posEquipJeter - direction

        if isinstance(theGame().floor.get(posEquipJeter),
                      Pieges):  ### si c'est un piege on remplacera le piege par l'element envoyé pour pas
            if Archet == None:
                theGame().floor.rm(
                    posEquipJeter)  ### faire reperer le piege sinon ce n'est pas un piege invisible on renvoie donc la pos
            return posEquipJeter

        if posEquipJeter != posHero:  ###sinon elle renvoit la pos max avant de sortir de la map ou de rencontrer un element
            return posEquipJeter
        if Archet == None:
            return theGame().addMessage("Vous ne pouvez pas envoyer d'équipement dans cette direction.")

    def JetBis(self, ChoixEquip, ChoixHeroDirec, NonUtilisable=None):
        ###Cette methode a ete faite spcialemnt pour completer JetUtilisation pour pas la rendre trop longue est complexe
        ## Elle nous permet de positionner un equipment à une position maximal en enchainant une direction avant de rencontrer un element
        ### ou d'appliquer l'equipment à un monstre si elle en rencontre un
        posMaxouCreatureToucher = self.JetPrincipal(ChoixHeroDirec.abbrv)
        if NonUtilisable == True:
            posMaxouCreatureToucher = self.JetPrincipal(ChoixHeroDirec.abbrv, None, True)
        if isinstance(posMaxouCreatureToucher,
                      Coord):  ##si posjet nous renvoie une position alors on place l'equipement choisit a cette pos
            if NonUtilisable == None:
                theGame().addMessage("Vous avez lâché votre " + ChoixEquip.name + " " + ChoixHeroDirec.name + ".")
                theGame().floor.put(posMaxouCreatureToucher, ChoixEquip)
            elif not isinstance(ChoixEquip, Armes) or ChoixEquip.ArmesJet != None:
                theGame().addMessage("On l'a donc déposé juste devant ce dernier.")
                theGame().floor.put(posMaxouCreatureToucher, ChoixEquip)
            theGame().hero.DetruireEquip(ChoixEquip)  ## et on l'enleve de l'inventaire

        if isinstance(posMaxouCreatureToucher,
                      Creature):  ##si posjet renvoie une creature alors on applique cette equipement a cette creature
            theGame().addMessage(
                "Vous avez choisi de lacher votre " + ChoixEquip.name + " à " + posMaxouCreatureToucher.name + ".")
            utilisation = ChoixEquip.use(posMaxouCreatureToucher)
            if utilisation == False or utilisation == None:  ## si l'objet n'est pas utilisable par la creature on l'envoie juste devant
                return posMaxouCreatureToucher
            theGame().hero._inventory.remove(ChoixEquip)

    def JetUtilisation(self):
        ### Cette methode va nous permettre de demander au joueur ce qu'il veut envoyer comme equipement et ou il veut l'envoyer pour ensuite appeller
        ## la methode jetbis
        ## Elle va permettre egalement au Archet de reperer quand le hero est dans leurs ligne de mire pour leurs enlever des degats

        ### Premier if sert au hero à envoyer un equipement
        if isinstance(self, Hero):
            ChoixEquip = theGame().select(self._inventory, "Quel élément de votre inventaire voulez vous envoyer?\n")
            if not isinstance(ChoixEquip, Element):
                return None
            ChoixHeroDirec = theGame().select(theGame().DirectionProposer, "Dans quel direction ?\n")

            if not isinstance(ChoixHeroDirec, Element):
                return None
            jetfinal = self.JetBis(ChoixEquip, ChoixHeroDirec)
            if isinstance(jetfinal,
                          Creature):  ##Si l'equipement n'est pas applicable sur la creature en renvoie l'equipement pour le deposer juste devant
                self.JetBis(ChoixEquip, ChoixHeroDirec, True)



        ### ce elif sert au archer pour envoyer des deagts au heros si il est dans leurs ligne de mire (aucun obstacle devant, meme salle):
        elif isinstance(self, Creature):

            for k in theGame().DirectionProposer:  ### ici l'archet va verifier si le hero est dans sa ligne de mire, en appelant toute les direction possible
                HeroDetecter = self.JetPrincipal(k.abbrv,
                                                 True)  ##dans JetPrincipal qui permet egalement de verifier si le hero est dans la ligne de mire
                if not isinstance(HeroDetecter, Coord):  ## en fonction de la direction
                    if HeroDetecter == True:  ##si oui on enleve de la vie au hero
                        return theGame().hero.meet(self)


class Hero(Creature):
    def __init__(self, name="Hero", hp=10, abbrv="@", strength=2):
        Creature.__init__(self, name, hp, abbrv, strength)
        self._inventory = []
        self.creatureTue = 0
        self.xp = 0
        self.niveau = 1
        self.hpmax = hp
        self.XPnecessaire = "?"
        self.Or = 0  ### Grace a cette instance nous allons comptez l'or à part et non pas dans l'inventaire
        self.ArmesEquiper = "Aucune"  ### Cette instance nous permettra de savoir quel arme est utilisé par le hero
        self.MonterNiveau()

    def take(self, elem):
        if not (isinstance(elem, Equipment)):
            raise TypeError("not an equipment")


        elif elem.name == "Or":  ### Ce elif nous permet de comptez l'or prit
            self.Or = self.Or + 1
            return True

        elif len(self._inventory) < 9:  ### Ce elif nous permet de verifier si il y a moins de 9 equipement
            self._inventory.append(elem)  ### dans l'inventaire pour pouvoir rajouter ce dernier
            return True  ### sinon le else nous informe qu'il y a plus de place dans l'inventaire
        else:
            theGame().addMessage("Vous n'avez plus de place dans l'inventaire malheuresement...")
            return False

    def SeDesequiper(self):
        ## cette methode permet de se desequiper d'une arme avec y
        if isinstance(self.ArmesEquiper, Armes):
            self._inventory.append(self.ArmesEquiper)
            ArmeUtilisé = self.ArmesEquiper
            self.ArmesEquiper = "Aucune"
            return theGame().addMessage("Vous vous êtes desequipé de " + ArmeUtilisé.name + ".")
        return theGame().addMessage(
            "Vous n'etes équipé d'aucune arme, vous ne pouvez donc pas utiliser cette fonction.")

    def fullDescription(self):
        res = ""
        for k in self.__dict__:
            if k != "_inventory":
                res = res + "> " + str(k) + " : " + str(self.__dict__[k]) + '\n'
        res = res + '\n' + "> " + str("INVENTORY") + " : " + str([x.name for x in self._inventory])
        return res

    def use(self, item):
        try:
            if not isinstance(item, Equipment):
                raise TypeError("Not a Equipment")
            if item not in self._inventory:
                raise ValueError("Not in inventory")
            if item.use(self):
                self._inventory.remove(item)
        except:
            pass

    ### On modifie la methode use en creant une exception de facon a ce que lorsque le hero selectione un equipment qui n'est
    ### pas present il n'y ai pas d'erreur et qu'il sorte de la selection pour pouvoir continuer de jouer
    def DetruireEquip(self, elem):
        ### Methode permettant de detruire un element (juste l'enleve de l'inventaire)
        if isinstance(elem, Element):
            self._inventory.remove(elem)
            theGame().addMessage(elem.name + " a été retiré de votre inventaire.")

    ### Nous creons mnt une methode pour permettre au heros d'augmenter en niveau à partir d'un certains nombre d'XP
    def MonterNiveau(self):
        ### Avec ce calcul on decide que le nombre d'Xp necessaire pour monter en niveau depend du niveau du heros
        ### plus le hero a un haut niveau plus il est difficile pour lui de monter à un niveau au dessus

        self.XPnecessaire = self.niveau * 200
        if self.xp >= self.XPnecessaire:
            self.niveau += 1
            self.strength += 2
            self.hpmax += 6
            self.hp = self.hpmax
            self.xp = 0
            theGame().addMessage("Bravo vous êtes au niveau superieur ! Votre puissance est maintenant de "
                                 + str(self.strength) + " et vos points de vie max de " + str(self.hp) + ".")

    #### A chaque fois que le heros monte de niveau il augmenteson niveau de vie de force etc et son exp revient a zero

    def Tir(self):
        if isinstance(self.ArmesEquiper, Armes):
            if self.ArmesEquiper.ArmesJet != None:
                ChoixHeroDirec = theGame().select(theGame().DirectionProposer)

                if not isinstance(ChoixHeroDirec, Element):
                    return None
                TirAtteintCrea = self.JetPrincipal(
                    ChoixHeroDirec.abbrv)  ##JetPrincipal permet egalement de verifier si une creature est dans la ligne de mire du hero
                ArmeEquiper = theGame().hero.ArmesEquiper
                if not isinstance(TirAtteintCrea, Coord):  ## en fonction de la direction choisit par le hero
                    if isinstance(TirAtteintCrea, Creature):  ##si oui on enleve la vie a la creature
                        res = TirAtteintCrea.meet(theGame().hero, True)
                        ##ArmeEquiper=theGame().hero.ArmesEquiper
                        if ArmeEquiper.utilisationUnique == True:  ### si l'arme utilisé est a utiliation unique on la retire de
                            theGame().addMessage(
                                ArmeEquiper.name + " à été retiré de l'inventaire.")  ## de l'inventaire
                            theGame().hero.ArmesEquiper = "Aucune"

                        if res == True:
                            theGame().floor.rm(theGame().floor.pos(TirAtteintCrea))
                            return res
                        return res
                if ArmeEquiper.utilisationUnique == True:  ##si le tir est rater on enleve quand meme l'arme si elle est a utilisation unique
                    theGame().addMessage(ArmeEquiper.name + " à été retiré de l'inventaire.")
                    theGame().hero.ArmesEquiper = "Aucune"
                theGame().addMessage("Votre tir n'a touché aucun monstre.")
                return True  ##on retourne true pour que le jeux puissent continuer meme si personne à été toucher (c'est a dire que les monstres  bougent)
                ##on utilisera ces return plus tard dans play
            return theGame().addMessage("Vous n'êtes pas équipé d'une arme permettant de tirer de loin.")
        return theGame().addMessage("Veuillez vous équiper d'une arme, avant d'utiliser cette fonction.")


class Coord():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if other == None:
            return False
        elif self.x is other.x and self.y is other.y:
            return True
        return False

    def __repr__(self):
        return "<" + str(self.x) + "," + str(self.y) + ">"

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)

    def distance(self, other):
        return math.sqrt(math.pow(other.x - self.x, 2) + math.pow(other.y - self.y, 2))

    def Diagonales(self, other):
        ### Ici nous avons créer une methode pour permettre le deplacement en diagonales au monstres, methode qui est lié à la
        ### methode de direction noramale d'origine
        prmDepl = self.direction(other, True)  ### il se peut que les monstres ne bouge pas a cause des pieges invisible
        DelpAnticipé = self.__add__(prmDepl).direction(other, True)
        if DelpAnticipé.__add__(prmDepl) in [Coord(1, 1), Coord(-1, 1), Coord(1, -1), Coord(-1, -1)]:
            return DelpAnticipé.__add__(prmDepl)
        return prmDepl

    ### Le fonctionnement est simple on anticipe un deplacement à l'avance, pour que si les deux deplacements prévus
    # cumulé forme un deplacement en diagonale, on realise directement un deplacement en diagonales

    def direction(self, other, testDiag=None):
        ### Pour ne pas que le programme ne mette une erreur il faut que la distance entre le monstre et le hero soit d'au moins 1
        ### pour pouvoir utilisé le deplacement diagonale pour pas provoquer d'erreur, car en anticipant lorsque les deux sont
        ### cote a cote l'anticipation etudie le fait qu'il soit l'un sur l'autre, ce qui fait une erreur
        if self.distance(other) > 1 and testDiag == None:
            if self.Diagonales(other) != None:  ## Ici on fait en sorte que la diagonales soit utilisé seulement si
                return self.Diagonales(
                    other)  ## c'est posssible (si elle raccourci le trajet) sinon on utilise la direction normale
            return self.direction(other, True)
        cos = self.__sub__(other).x / abs(self.distance(other))
        if cos > 1 / math.sqrt(2):

            return Coord(-1, 0)
        elif cos < -1 / math.sqrt(2):
            return Coord(1, 0)
        elif self.__sub__(other).y > 0:
            return Coord(0, -1)
        else:
            return Coord(0, 1)


class Map():
    ground = "."
    dir = {'z': Coord(0, -1), 's': Coord(0, 1), "d": Coord(1, 0), "q": Coord(-1, 0)}
    empty = " "

    def __init__(self, size=20, hero=None, nbrooms=7):
        self.nbrooms = nbrooms
        self._roomsToReach = []
        self._rooms = []
        self.size = size
        if hero == None:
            hero = Hero()
        self.hero = hero
        self._mat = []
        for k in range(self.size):
            self._mat.append([Map.empty] * self.size)
        self.generateRooms(nbrooms)
        self.reachAllRooms()
        self._mat[(self._rooms[0].c1 + self._rooms[0].c2).y // 2][(self._rooms[0].c1 + self._rooms[0].c2).x // 2] = hero
        self._elem = {}
        for k in range(self.size):
            for i in range(self.size):
                if self._mat[k][i] != Map.ground and self._mat[k][i] != Map.empty:
                    self._elem[self._mat[k][i]] = Coord(i, k)
        for k in self._rooms:
            k.decorate(self)
        self.afficheEscaliers()  ### Ici on affiche des ecsaliers dans toutes les map
        self.afficheBoutiques()  ### Ici on affiche une boutique dans toutes les map
        self.afficheCoffre()  ### Ici on affiche un coffre dans toutes les map
        self.ClesTrouver = random.randint(1,
                                          self.NombredeMonstre())  ### Ici on cache la clés dans un des monstres au hasard
        self.affichePieges()  ###Ici avec cette instance on place les pieges dans la map
        self.NombreMonstreXPtotal()

    def __repr__(self):
        res = ""
        for k in range(self.size):
            for i in range(self.size):
                res = res + str(self._mat[k][i])
            res = res + '\n'
        return res

    def __len__(self):
        return self.size

    def __contains__(self, item):
        if isinstance(item, Coord):
            return item.x in range(self.size) and item.y in range(self.size)

        for k in range(self.size):
            for i in range(self.size):
                if self._mat[k][i] == item:
                    return True
        return False

    def afficheEscaliers(self):
        try:
            ### On place les escaliers dans une salle au hasard au centre
            salle = random.choice(self._rooms)
            ### Si les coordonnées trouvée correspondent au sol et à une position vide (ground) au milieu de la salle,
            ### on y place (put) alors les escaliers
            if self.get(Room.center(salle)) == self.ground:
                self.put(Room.center(salle), Escaliers())
            ### Sinon on rappel la methode pour trouver une autres coordonée valide et vide
            else:
                self.afficheEscaliers()
        except:
            theGame().buildFloor()

    ### On creé une exception au cas ou il y a une erreur de recursion maximal car comme nous avons les escalier et
    ### et la boutique au milieu des salle, il se peut que la map soit trop petite et donc qu'il n'est pas assez de room
    ### pour mettre ces dernieres au milieu des room, ducoup dans ce cas là on creer une nouvelles carte jusqu'a trouver
    ### une carte ou la boutique et les escaliers peuvent être mise.

    def afficheBoutiques(self):
        try:
            ### On place la boutique dans une salle au hasard au centre
            salle = random.choice(self._rooms)
            ### Si les coordonnées trouvée correspondent au sol et à une position vide (ground) au mileu de la salle,
            ### on y place (put) alors la boutique
            if self.get(Room.center(salle)) == self.ground:
                self.put(Room.center(salle), Boutique())
            ### Sinon on rappel la methode pour trouver une autres coordonée valide et vide
            else:
                self.afficheBoutiques()
        except:
            theGame().buildFloor()

    ### On creé une exception au cas ou il y a une erreur de recursion maximal car comme nous avons les escalier et
    ### et la boutique au milieu des salle, il se peut que la map soit trop petite et donc qu'il n'est pas assez de room
    ### pour mettre ces dernieres au milieu des room, ducoup dans ce cas là on creer une nouvelles carte jusqu'a trouver
    ### une carte ou la boutique et les escaliers peuvent être mise.

    def afficheCoffre(self):
        salle = random.choice(self._rooms)
        testCoordHasrd = Room.randCoord(salle)
        ### On choisit une salle de la carte au hasard
        ### On choisit egalement des coordonnées au hasard et si celles ci correspondent au sol et à une position vide (ground),
        ### on y place (put) alors le coffre
        if self.get(testCoordHasrd) == self.ground:
            self.put(testCoordHasrd, Coffre())
        ### Sinon on rappel la methode pour trouver une autres coordonée valide et vide
        else:
            self.afficheCoffre()

    def get(self, c):
        self.checkCoord(c)
        return self._mat[c.y][c.x]

    def pos(self, e):
        self.checkElement(e)
        return self._elem[e]

    def put(self, c, e):
        self.checkCoord(c)
        self.checkElement(e)
        if self._mat[c.y][c.x] != self.ground:
            raise ValueError('Incorrect cell')
        if self._elem.get(e):
            raise KeyError('Already placed')
        self._mat[c.y][c.x] = e
        self._elem[e] = c

    def rm(self, c):
        self.checkCoord(c)
        del self._elem[self._mat[c.y][c.x]]
        self._mat[c.y][c.x] = self.ground

    def move(self, e, way):
        """Moves the element e in the direction way."""
        orig = self.pos(e)
        dest = orig + way
        if dest in self:
            if self.get(dest) == Map.ground:
                self._mat[orig.y][orig.x] = Map.ground
                self._mat[dest.y][dest.x] = e
                self._elem[e] = dest
            elif self.get(dest) != Map.empty and self.get(dest).meet(e) and self.get(dest) != self.hero:
                self.rm(dest)

    def addRoom(self, room):
        self._roomsToReach.append(room)
        for k in range(room.c1.y, room.c2.y + 1):
            for i in range(room.c1.x, room.c2.x + 1):
                self._mat[k][i] = self.ground

    def randGround(self):
        pos = Coord(random.randint(0, len(self._mat) - 1), random.randint(0, len(self._mat) - 1))
        while self.get(pos) != ".":
            pos = Coord(random.randint(0, len(self._mat) - 1), random.randint(0, len(self._mat) - 1))
        return pos

    def findRoom(self, coord):
        for k in self._roomsToReach:
            if Room.intersect(k, Room(coord, coord)):
                return k
        return False

    def intersectNone(self, room):
        for k in self._roomsToReach:
            if Room.intersect(k, room):
                return False
        return True

    def dig(self, coord):
        self._mat[coord.y][coord.x] = self.ground
        if self.findRoom(coord) != False and self.findRoom(coord) not in self._rooms:
            self._rooms.append(self.findRoom(coord))
            self._roomsToReach.remove(self.findRoom(coord))

    def corridor(self, start, end):
        if start.y < end.y:
            for w in range(start.y, end.y + 1):
                self.dig(Coord(start.x, w))
        if start.y > end.y:
            for t in reversed(range(end.y, start.y + 1)):
                self.dig(Coord(start.x, t))
        if start.x < end.x:
            for k in range(start.x, end.x + 1):
                self.dig(Coord(k, end.y))
        if start.x > end.x:
            for r in reversed(range(end.x, start.x + 1)):
                self.dig(Coord(r, end.y))

    def reach(self):
        room = random.choice(self._rooms)
        roomr = random.choice(self._roomsToReach)
        coordmilieuroom = Coord((room.c1 + room.c2).x // 2, (room.c1 + room.c2).y // 2)
        coordmilieuroomr = Coord((roomr.c1 + roomr.c2).x // 2, (roomr.c1 + roomr.c2).y // 2)
        self.corridor(coordmilieuroom, coordmilieuroomr)

    def reachAllRooms(self):
        self._rooms.append(self._roomsToReach.pop(0))
        while len(self._roomsToReach) != 0:
            self.reach()

    def randRoom(self):
        startx = random.randint(0, self.size - 3)
        starty = random.randint(0, self.size - 3)
        largeur = random.randint(3, 8)
        hauteur = random.randint(3, 8)
        endx = min(self.size - 1, startx + largeur)
        endy = min(self.size - 1, starty + hauteur)
        return Room(Coord(startx, starty), Coord(endx, endy))

    def generateRooms(self, n):
        for k in range(n):
            essai = self.randRoom()
            if self.intersectNone(essai):
                self.addRoom(essai)

    def checkCoord(self, c):
        if not (isinstance(c, Coord)):
            raise TypeError('Not a Coord')

        if c.x not in range(self.size) or c.y not in range(self.size):
            raise IndexError('Out of map coord')

    def checkElement(self, c):
        if not (isinstance(c, Element)):
            raise TypeError('Not a Element')

    def moveAllMonsters(self):
        """Moves all monsters in the map.
            If a monster is at distance lower than 6 from the hero, the monster advances."""
        h = self.pos(self.hero)
        for e in self._elem:
            c = self.pos(e)
            if isinstance(e, Creature) and e != self.hero:
                if e.name == "Sniper":  ## ici on rajoute un if, au cas ou la creature est un Archet, la creature ne bougera pas
                    e.JetUtilisation()  ## comme les autres creature et verifera si le hero est dans sa ligne de mire pour le frapper (avec JetUtilisation)

                elif c.distance(h) < 6:
                    d = c.direction(h)
                    if self.get(c + d) in [Map.ground, self.hero]:
                        self.move(e, d)

    ### Cette methode nous permet de comptez le nombre de monstre presents dans la map pour pouvoir caché la clé dans l'un d'eux
    def NombredeMonstre(self):
        res = 0
        for k in self._elem:
            if isinstance(k, Creature):
                res = res + 1
        return res - 1

    ### Cette methode calcule le nombre d'XP maximal pouvant encore etre gagner dans un étages
    def NombreMonstreXPtotal(self):
        res = 0
        for k in self._elem:
            if isinstance(k, Creature):
                res = res + (k.hpmax * 10)
            ### comme le hero est aussi une creature on l'enleve du calcul d'ou le deuxieme if
            if isinstance(k, Hero):
                res = res - (k.hpmax * 10)
        return res

    def affichePieges(self):
        ### Cette methode va nous permettre de placer les pieges dans la map dans une salle au hasard
        salle = random.choice(self._rooms)
        testCoordHasrd = Room.randCoord(salle)
        ### On met un nombre de pieges proportionel à l'aire de la salle grace à la methode qu'on a creer "AireRoom"
        for nbpiege in range(Room.AireRoom(salle) // 3):
            while self.get(
                    testCoordHasrd) != self.ground:  ### Boucle tant que l'on a pas trouver une coord valide (vide)
                testCoordHasrd = Room.randCoord(salle)
            self.put(testCoordHasrd, Pieges())


class Room():

    def __init__(self, c1, c2):
        self.c1 = c1
        self.c2 = c2

    def __repr__(self):
        return "[" + str(self.c1) + ", " + str(self.c2) + "]"

    def __contains__(self, item):
        return item.x in range(self.c1.x, self.c2.x + 1) and item.y in range(self.c1.y, self.c2.y + 1)

    def center(self):
        return Coord((self.c1.x + self.c2.x) // 2, (self.c1.y + self.c2.y) // 2)

    def AireRoom(self):
        ## on creer cette methode pour trouver l'aire d'une salle pour pouvoir placer un nombre de pieges proportionnel
        ## a la taille de la salle
        Largeur = self.c2.x - self.c1.x
        Longeur = self.c2.y - self.c1.y
        Aire = Largeur * Longeur
        return Aire

    def intersect(self, other, compteur=None):
        if (self.c1.x in range(other.c1.x, other.c2.x + 1) and self.c1.y in range(other.c1.y, other.c2.y + 1)) or (
                self.c2.x in range(other.c1.x, other.c2.x + 1) and self.c2.y in range(other.c1.y, other.c2.y + 1)):
            return True
        elif compteur == None:
            return other.intersect(self, compteur=1)
        return False

    def randCoord(self):
        return Coord(random.randint(self.c1.x, self.c2.x), random.randint(self.c1.y, self.c2.y))

    def randEmptyCoord(self, map):
        c = self.randCoord()
        if map.get(c) == map.ground and c != self.center():
            return c
        return self.randEmptyCoord(map)

    def decorate(self, map):
        map.put(self.randEmptyCoord(map), theGame().randEquipment())
        map.put(self.randEmptyCoord(map), theGame().randMonster())


class Game(object):
    elementmap = {0: [Equipment("Clé", imageAss="Cles.png"),
                      Escaliers("Escaliers", imageAss="Escalier.png"),
                      Boutique("Boutique", imageAss="Boutique.png"),
                      Coffre("Coffre", imageAss="Coffre.png"),
                      Pieges("Pieges invisible", imageAss="Pieges.png")]}

    equipments = {0: [Equipment("Potion Santé", "!", lambda item, creature: heal(creature), imageAss="Potion.png"),
                      Equipment("Potion Vision", "V", lambda hero: affichepiege(), imageAss="PotionVision.png"),
                      Equipment("Or", "o", imageAss="Or.png"),
                      Armes("Couteaux", 1, "d", True, True, imageAss="Couteaux.png")],
                  1: [Equipment("bouclier de lancer", imageAss="Bouclier.png"),
                      Armes("Hache de lancé", 3, "h", True, True, imageAss="Hache.png"),
                      Armes("Machette", 2, "m", imageAss="Machette.png"),
                      Equipment("Potion Telep", "!L", lambda item, creature: teleport(creature, True),
                                imageAss="Portoloin2.png")
                      ],
                  2: [Armes("P-39", 3, "p", True, imageAss="P-39.png"),
                      Armes("Grenade", 3, "g", True, True, imageAss="Grenade.png")],
                  3: [Equipment("Portoloin", "w", lambda x, creature: teleport(creature, None),
                                imageAss="Portoloin.png"),
                      Armes("Fusil à Pompe", 4, "f", True, imageAss="Pompe.png"),
                      Armes("Uzi", 5, "k", True,
                            imageAss="Uzi.png")]}  ##On a rajouter differente armes pouvant être utilisé, (non)lancable et usageunique ou non

    monsters = {0: [Creature("GB1", 3, imageAss="Goblin1.png"),
                    Creature("GB2", 3, imageAss="Goblin2.png"),
                    Creature("Fatigué", 1, imageAss="Fatigué.png"),
                    Creature("Provincial", 2, "W", imageAss="Provincial.png"),
                    Creature("Sniper", 3, imageAss="Sniper.png")],
                1: [Creature("Anorexique", 6, strength=2, imageAss="Anorexique.png"),
                    Creature("GB3", 4, imageAss="Goblin3.png"),
                    Creature("Jeune Chinois", 10, imageAss="Chinois.png"),
                    Creature("Qatari", 2, imageAss="Qatari.png")],
                5: [Creature("LeBlond", 15, strength=3, imageAss="LeBlond.png"),
                    Creature("Poulpe", 20, strength=3, imageAss="Poulpe.png")]}  ## on ajoute la creature Archet

    DirectionProposer = [Element(" ↓ ", Coord(0, 1)), Element(" ↑ ", Coord(0, -1)),
                         Element(" → ", Coord(1, 0)),
                         Element(" ← ", Coord(-1, 0)),
                         Element(" ↖ ", Coord(-1, -1)),
                         Element(" ↗ ", Coord(1, -1)),
                         Element(" ↘ ", Coord(1, 1)),
                         Element(" ↙ ", Coord(-1, 1))]
    ### On stoke les choix demandé dans name (de Element) pour pouvoir utilisé la fonction select sans la modifier et laisser choisir le hero
    ### On utilise abbrv pour stocker les coordonée de la direction choisit pour pouvoir l'utilisé ensuite dans posJet et d'autre methode

    _actions = {'Up': lambda hero: theGame().floor.move(hero, Coord(0, -1)),
                'Down': lambda hero: theGame().floor.move(hero, Coord(0, 1)),
                'Left': lambda hero: theGame().floor.move(hero, Coord(-1, 0)),
                'Right': lambda hero: theGame().floor.move(hero, Coord(1, 0)),
                'q': lambda hero: theGame().floor.move(hero, Coord(-1, -1)),
                'e': lambda hero: theGame().floor.move(hero, Coord(1, -1)),
                'c': lambda hero: theGame().floor.move(hero, Coord(1, 1)),
                'z': lambda hero: theGame().floor.move(hero, Coord(-1, 1)),
                # 'i': lambda hero: theGame().affichepiege(),
                'k': lambda hero: theGame().replay(),
                'space': lambda hero: None,
                'u': lambda hero: hero.use(theGame().select(hero._inventory)),
                'y': lambda hero: theGame().hero.SeDesequiper(),
                't': lambda hero: theGame().hero.Tir(),
                'l': lambda hero: theGame().hero.DetruireEquip(theGame().select(hero._inventory)),
                'j': lambda hero: theGame().hero.JetUtilisation(),
                'f': lambda hero: sys.exit()}

    ## Le "f" permet ici de pouvoir sortir completement du jeux du jeux completement car le "k" permet simplement de recommencer le jeux
    ## Le 'l' nous permet de detruire un equipment de l'inventaire

    def __init__(self, hero=None, level=1):
        if hero == None:
            hero = Hero()
        self.hero = hero
        self.level = level
        self.floor = None
        self._message = []
        self.fen_princ = Tk()
        self.fen_princ.title("La Tour Infinie")
        self.fen_princ.geometry("610x690")
        self.monCanvas = Canvas(self.fen_princ, bg='#1B2326', scrollregion=(-400, -400, 1000, 1000))
        self.yScrollBar = Scrollbar(self.monCanvas, orient=VERTICAL)
        self.yScrollBar.config(command=self.monCanvas.yview)
        self.xScrollBar = Scrollbar(self.monCanvas, orient=HORIZONTAL)
        self.xScrollBar.config(command=self.monCanvas.xview)
        self.monCanvas.config(yscrollcommand=self.yScrollBar.set, xscrollcommand=self.xScrollBar.set)
        self.widgetMessage = Label(self.fen_princ, textvariable=self.readMessages(), fg='white', bg='#154e72')
        self.widgetinfoHetM = Frame(self.fen_princ)
        self.widgetReglCom = Frame(self.fen_princ)
        self.widgetMessage.pack(expand=0, fill=X)
        self.monCanvas.pack(expand=True, fill=BOTH)
        self.widgetinfoHetM.pack(expand=0, fill=X, side="bottom")
        self.infohero = Label(self.widgetinfoHetM, text="~~Information Hero~~", bg='#154e72', fg='white')
        self.infomap = Label(self.widgetinfoHetM, text="~~Information Map~~", bg='#154e72', fg='white')
        self.infohero.pack(side="left", fill="both", expand=True)
        self.infomap.pack(side="right", fill="both", expand=True)
        self.Photoperso1 = self.resizeimg("Hero1.png", 60)
        self.indication = self.resizeimg("Indication.png", 15)
        self.Photoperso1jeux = self.resizeimg("Hero1.png")
        self.Photoperso2jeux = self.resizeimg("Hero2.png")
        self.Photoperso2 = self.resizeimg("Hero2.png", 60)
        self.Pagedacce = Label(self.monCanvas, text="\n\n\n\nBienvenue dans la Tour Infinie\n\n"
                                                    "Ton but sera de monter le plus haut possible !! "
                                                    "Pour ce faire tu devras accéder\naux escaliers qui se "
                                                    "situent quelque part dans la Map. Des monstres sont placés\n"
                                                    "partout dans la Map et sont à chaque étage de plus en plus fort."
                                                    "Tu devras les éliminer\nlorsqu'ils sont sur ton chemin. Pour cela, rien de plus "
                                                    "simple diriges toi dans leurs \ndirections lorsqu'ils sont à proximité et ainsi "
                                                    "tu leurs infligeras des dégâts.\n Des équipements (armes de poing et de lancer, potions etc...) sont également "
                                                    "\nplacer dans la Map, tu peux les prendre, en passant dessus. Plus tu élimineras de \n"
                                                    "monstres plus ton niveau augmentera et donc ta puissance et ta santé évolueront\n\n"
                                                    "Attention dans une pièce de chaque étage se trouvent des pièges invisibles,\n"
                                                    "plus l'étage est élevé, plus les dégâts de ces pièges sont importants."
                               , bg='#1B2326', fg='white')
        self.LogoJeux = self.resizeimg("Logo.png", 120)
        self.Pagedacce["compound"] = TOP
        self.Pagedacce["image"] = self.LogoJeux
        self.Pagedacce.pack(expand=True, fill=BOTH)
        self.PropHero = Frame(self.fen_princ)
        self.PropHero.pack(expand=0, fill=X, side=BOTTOM)
        self.Perso1 = Button(self.PropHero, text='Lancer le jeux',
                             command=lambda hero=self.Photoperso1jeux: self.ChooseHero(hero), image=self.Photoperso1)
        self.Perso2 = Button(self.PropHero, text='Lancer le jeux',
                             command=lambda hero=self.Photoperso2jeux: self.ChooseHero(hero), image=self.Photoperso2)
        self.ShowCom = Button(self.widgetReglCom, text='Choisis ton personnage pour commencer')
        self.Perso2.pack(side="left", fill=X, expand=True)
        self.Perso1.pack(side="right", fill=X, expand=True)
        self.widgetReglCom.pack(expand=0, fill=X)
        self.ShowCom.pack(expand=0, fill=X)
        self.Indication = Toplevel(self.fen_princ)
        self.ShowIndic = Button(self.widgetReglCom, text='   Indication', command=self.Indication.deiconify)
        self.Indication.geometry("395x400")  # Size of the window
        self.Indication.title("Commande")
        self.IndicationText = Label(self.Indication, text="\n--- Indications ---\n\n"
                                                          "À chaque étage se trouvent une boutique et un coffre.\n"
                                                          "Pour pouvoir ouvrir le coffre et obtenir un équipement\n"
                                                          "spécial il te faudra trouver une clé cachée dans un des\n"
                                                          "monstres de l'étage. Après l'avoir éliminé, tu recevras\n"
                                                          "directement la clé, dans ton inventaire, pour pouvoir ouvrir\n"
                                                          "le coffre. Dans la boutique tu pourras acheter tous\n"
                                                          "les équipements du jeu, grâce aux pièces d'or que tu auras \n"
                                                          "trouvé un peu partout dans la tour. Tu pourras également\n"
                                                          "vendre tes équipements à la boutique contre de l'or. Certains\n"
                                                          "monstres peuvent t’affliger des dégâts à distances ce sont\n"
                                                          "les snipers, ils sont immobiles. Il existe des potions pour se\n"
                                                          "téléporter (Portoloin) et pour reprendre sa santé (Potion).\n"
                                                          "Pense à jeter tes équipements en direction des monstres pour\n"
                                                          "les bloquer dans leurs lancés et ainsi les empêcher de se \n"
                                                          "déplacer vers toi et de t’infliger des dégâts de loin.\n"
                                                          "L'équipement 'Bouclier’ a été conçu spécialement pour.\n"
                                                          "Pour pouvoir repérer les pièges invisibles, tu peux utiliser \n"
                                                          "la 'Potion Vision' qui les rend visibles. ",

                                    bg='#1B2326', fg='white')
        self.Commande = Toplevel(self.fen_princ)
        self.Commande.geometry("395x400")  # Size of the window
        self.Commande.title("Commande")
        self.CommandeText = Label(self.Commande, text="\n--- Commandes de jeu ---\n\n"
                                                      "Déplacements:\n\n"
                                                      "Utilise les flèches de ton clavier,\n"
                                                      "pour les déplacements classiques, en plus :\n"
                                                      "e: (diagonale) ↗ | c: (diagonale) ↘ \n"
                                                      "z: (diagonale) ↙ | q: (diagonale) ↖ \n\n"
                                                      "Actions:\n\n"
                                                      "u: s'équiper d'une arme | j: jeter un équipement \n"
                                                      "l: détruire un équipement | espace: passe le tour\n"
                                                      "t: lancer ou tirer avec une arme | y: se déséquiper d'une arme\n\n"
                                                      "Autres:\n\n"
                                                      "| Appuyer sur k pour recommencer une nouvelle partie |\n"
                                                      "|         Appuyer sur f pour quitter le jeu         |\n"
                                  , bg='#1B2326', fg='white')
        self.CommandeText.pack(expand=True, fill=BOTH)
        self.IndicationText.pack(expand=True, fill=BOTH)
        self.Indication.withdraw()
        self.Commande.withdraw()
        self.fen_princ.protocol("WM_DELETE_WINDOW", sys.exit)
        self.Commande.protocol("WM_DELETE_WINDOW", self.Commande.withdraw)
        self.Indication.protocol("WM_DELETE_WINDOW", self.Indication.withdraw)
        self.elem = {}
        self.AffichePiege = False

    def affichepiege(self):
        self.AffichePiege = True

    def stockImage(self):
        for k in theGame().elementmap:
            for i in theGame().elementmap[k]:
                self.elem[i] = self.resizeimg(i.imageAss, 25)

        for k in theGame().equipments:
            for i in theGame().equipments[k]:
                self.elem[i] = self.resizeimg(i.imageAss, 25)

        for k in theGame().monsters:
            for i in theGame().monsters[k]:
                self.elem[i] = self.resizeimg(i.imageAss)

    def ChooseHero(self, herochose):
        self.hero.imageAss = herochose
        self.play()

    def TrouveNiveauEquip(self, elem):
        ### on creer cette methode qui nous trouve le niveau d'un equipment pour nous aider determiner le prix ce cette
        ### equipement dans la boutique
        for k in self.equipments:
            for x in self.equipments[k]:
                if x.name == elem.name:
                    return k

    def replay(self):
        self.fen_princ.destroy()
        self.__init__()
        theGame().stockImage()



    def buildFloor(self):
        self.floor = Map(hero=self.hero)
        self.dessin()

    def addMessage(self, msg):
        self._message.append(msg)

    def readMessages(self):
        res = ""
        for k in range(len(self._message)):
            if res == "":
                res = res + self._message.pop(0)
            else:
                res = res + "\n" + self._message.pop(0)
        return res

    def randElement(self, collection):
        X = int(random.expovariate(1 / self.level))
        for i in collection:
            if i <= X:
                res = i
        return copy.copy(random.choice(collection.get(res)))

    def randEquipment(self):
        return self.randElement(self.equipments)

    def randMonster(self):
        return self.randElement(self.monsters)

    def select(self, l, textafiche=""):
        if l == []:
            return theGame().addMessage("Votre inventaire est vide.")

        r = "| "
        for x in range(len(l)):
            if x % 4 == 0 and x != 0:
                r += "\n| " + str(x) + ": " + l[x].name + " | "
            else:
                r += str(x) + ": " + l[x].name + " | "

        try:
            sc = Screen()
            sc.setup(0, 0)
            choixHero = int(textinput("La Tour Infinie", textafiche + "Veuillez choisir un Index> \n" + r))
            sc.bye()
            return l[choixHero]
        except:
            theGame().addMessage("L'Index entré est invalide.")

    def resizeimg(self, imageUrl, size=40):
        image = Image.open(imageUrl)
        image = image.resize((size, size), Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)

    def dessin(self):
        longeurCase = 23
        GraphJeux = self.floor._mat
        for y in range(len(GraphJeux)):
            for x in range(len(GraphJeux[y])):
                if GraphJeux[y][x] != " " or isinstance(GraphJeux[y][x], Pieges):
                    self.monCanvas.create_rectangle(20 + longeurCase * x, 20 + longeurCase * y,
                                                    20 + longeurCase * (x + 1), 20 + longeurCase * (y + 1),
                                                    outline="#000000", fill="#DCDCDC")

        for y in range(len(GraphJeux)):
            for x in range(len(GraphJeux[y])):

                if isinstance(GraphJeux[y][x], Element) and not (isinstance(GraphJeux[y][x], Pieges)) and GraphJeux[y][
                    x] != self.hero and self.AffichePiege == False:
                    for k in self.elem:
                        if GraphJeux[y][x].name == k.name:
                            if not (isinstance(GraphJeux[y][x], Creature)) or GraphJeux[y][x].name == "Sniper":
                                self.monCanvas.create_image(20 + longeurCase * (x + 0.47),
                                                            20 + longeurCase * (y + 0.42), image=self.elem[k])
                            else:
                                self.monCanvas.create_image(20 + longeurCase * (x + 0.5), 20 + longeurCase * (y),
                                                            image=self.elem[k])

                if isinstance(GraphJeux[y][x], Element) and GraphJeux[y][x] != self.hero and self.AffichePiege == True:
                    for k in self.elem:
                        if GraphJeux[y][x].name == k.name:
                            if not (isinstance(GraphJeux[y][x], Creature)) or GraphJeux[y][x].name == "Sniper":
                                self.monCanvas.create_image(20 + longeurCase * (x + 0.47),
                                                            20 + longeurCase * (y + 0.42), image=self.elem[k])
                            else:
                                self.monCanvas.create_image(20 + longeurCase * (x + 0.5), 20 + longeurCase * (y),
                                                            image=self.elem[k])

                if GraphJeux[y][x] == self.hero:
                    self.monCanvas.create_image(20 + longeurCase * (x + 0.5), 20 + longeurCase * (y),
                                                image=self.hero.imageAss)

        self.monCanvas.pack()

    def jeux(self, event):
        event = event.keysym
        if self.hero.hp > 0:
            if event not in Game._actions:
                theGame().addMessage("La touche entrée ne correspond à aucune actions")
            if event in Game._actions:
                actions = Game._actions[event](self.hero)
            if (event not in ["u", "l", "i", "j", "y"] and event in Game._actions):
                ### Ce if permet de bloquer le tour lorsque le hero utilise ou detruit un equipment ou que la lettre taper ne correspond a aucune action
                if event == "t" and actions == None:  ##si les tir n'en pas été possible on ne fait pas bouger les monstres
                    pass  ##cependant si les tir on été rater on les fait bouger
                self.floor.moveAllMonsters()  ### ou encore lorsque le hero verifie ces informations completes (les monstres ne se deplace pas)
            self.hero.MonterNiveau()
            self.widgetMessage.config(text=self.readMessages())
            self.infohero.config(text=self.infoHero())
            self.infomap.config(text="Etage : " + str(self.level))
            self.monCanvas.delete("all")
            self.dessin()
        else:
            self.widgetMessage.config(text='GAME OVER\nRéessayer:  appuyez sur k\nQuitter:  appuyez sur f')
            if event in ["f", "k"]:
                actions = Game._actions[event](self.hero)

    def infoHero(self):
        if isinstance(self.hero.ArmesEquiper, Armes):
            return self.hero.description() + "\n" + "Inventaire : " + str(
                self.hero._inventory) + "\n" + "Arme equipé : " + self.hero.ArmesEquiper.name + "\n" + "Niveau : " + str(
                self.hero.niveau) + "\n" + "XP : " + str(self.hero.xp) + "/" + str(
                theGame().hero.XPnecessaire) + "\n" + "Or : " + str(self.hero.Or)
        else:
            return self.hero.description() + "\n" + "Inventaire : " + str(
                self.hero._inventory) + "\n" + "Arme equipé : " + self.hero.ArmesEquiper + "\n" + "Niveau : " + str(
                self.hero.niveau) + "\n" + "XP : " + str(self.hero.xp) + "/" + str(
                self.hero.XPnecessaire) + "\n" + "Or : " + str(self.hero.Or)

    def play(self):
        self.Pagedacce.destroy()
        self.PropHero.destroy()
        self.ShowIndic.pack(side="left", fill=X, expand=True)
        self.ShowIndic["compound"] = LEFT
        self.ShowIndic["image"] = self.indication
        self.ShowCom["compound"] = LEFT
        self.ShowCom["image"] = self.indication
        self.ShowCom.config(text="   Commandes de jeu", command=self.Commande.deiconify)
        self.ShowCom.pack(side="right", fill=X, expand=True)
        self.buildFloor()
        self.yScrollBar.pack(side=RIGHT, fill=Y)
        self.xScrollBar.pack(side=BOTTOM, fill=X)
        self.infohero.config(text=self.infoHero())
        self.infomap.config(text="Etage : " + str(self.level))
        self.fen_princ.bind('<Any-KeyPress>', self.jeux)


def theGame(game=Game()):
    return game


theGame().stockImage()
theGame().fen_princ.mainloop()
theGame()

