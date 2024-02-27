from xrdpattern import XrdPattern

if __name__ == "__main__":
    xrd_pattern = XrdPattern(filepath="/home/daniel/test/local/parsed/Simon_Schweidler_Ben_Breitung_2024_02_14_4/data/daten_gallium/Alaa/LLZNb06Gd02In02O_l.raw")
    print(xrd_pattern.twotheta_to_intensity)
    print(xrd_pattern.__dict__)
    print(xrd_pattern.to_json())
    xrd_pattern.export(filepath='test')