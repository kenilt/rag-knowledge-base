import marqo

mq = marqo.Client()
# mq.create_index("my_knowledge_base")
# documents = [
#     {"title": "ABOUT HALIO", "content": "Halio is skincare and dental brand from the United States. The company's product line integrates innovative design and modern technology, providing optimal efficiency, and helping you always to be bright and radiant. Let's refer some of the main technologies applied in our product below!"},
#     {"title": "SONIC WAVE", "content": "Sonic Wave goes deep to remove 99.5% dirt, oil, sweat, dead skin cells, or even makeup residue. Halio will leave your skin a refreshing feel without causing any irritation."},
#     {"title": "ION GALVANIC AND F-VIBRATIONS", "content": "The principle of charges repelling and attracting ion emission to remove toxins, grease, and dirt. Besides, the high-frequency vibrations will help nutrients absorb better into the skin, improve the skin from the inside out."},
#     {"title": "INTENSE PULSED LIGHT (IPL)", "content": "Halio IPL Hair Removal Device is designed to deliver an effective long-term hair removal with visible results in just a few uses, regarding undesired hair growth without causing stubble, ingrown hairs, redness, or other irritation - and it's pain-free!"},
#     {"title": "NANO BLUE LIGHT", "content": "The most modern light with a wavelength of 490±10mm maximizes the activation of Hydrogen Peroxide active ingredient. Then it safely and effectively removes stains on the teeth's surface as well as decolorizes the deep section of the teeth"}
# ]
# mq.index("my_knowledge_base").add_documents(documents, tensor_fields=["content"])

# results = mq.index("my_knowledge_base").search(
#     q="What is Halio?"
# )
# print(results)


# mq.create_index("my-first-index")

# mq.index("my-first-index").add_documents([
#     {
#         "Title": "The Travels of Marco Polo",
#         "Description": "A 13th-century travelogue describing Polo's travels"
#     },
#     {
#         "Title": "Extravehicular Mobility Unit (EMU)",
#         "Description": "The EMU is a spacesuit that provides environmental protection, "
#                        "mobility, life support, and communications for astronauts",
#         "_id": "article_591"
#     }],
#     tensor_fields=["Description"]
# )

# results = mq.index("my-first-index").search(
#     q="What is the best outfit to wear on the moon?"
# )
# print(results)

# results = mq.index("doodoo_base").delete()
# print(results)

# all_docs = mq.index("doodoo_base").search("", limit=1000)
# print(all_docs)
