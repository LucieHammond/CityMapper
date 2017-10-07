# -*- coding: utf-8 -*-

dico = {"a":1, "b":2}
dico.update({})

text = u'{"address": "28 Bd de la R\xe9publique 92100 BOULOGNE BILLANCOURT"}'
print type(text)
print text

text2 = unicode(text)
print type(text2)

print text2