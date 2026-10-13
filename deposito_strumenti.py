import csv
from operator import attrgetter


class Strumento:
    def __init__(self, codice, tipo, marca, anno_acquisto, valore):
        self._codice = codice
        self._tipo = tipo
        self._marca = marca
        self._anno_acquisto = anno_acquisto
        self._valore = valore

    @property
    def codice(self):
        return self._codice

    @property
    def tipo(self):
        return self._tipo

    @property
    def marca(self):
        return self._marca

    @property
    def anno_acquisto(self):
        return self._anno_acquisto

    @property
    def valore(self):
        return self._valore

    def __str__(self):
        return f"[{self._codice}] {self._tipo} - {self._marca} ({self._anno_acquisto}) - €{self._valore:.2f}"

    def __repr__(self):
        return f"Strumento('{self._codice}', '{self._tipo}', '{self._marca}', {self._anno_acquisto}, {self._valore})"


class Prestito:
    def __init__(self, codice, data, id_strumento, cognome_allievo):
        self._codice = codice
        self._data = data
        self._id_strumento = id_strumento
        self._cognome_allievo = cognome_allievo

    @property
    def codice(self):
        return self._codice

    @property
    def data(self):
        return self._data

    @property
    def id_strumento(self):
        return self._id_strumento

    @property
    def cognome_allievo(self):
        return self._cognome_allievo

    def __str__(self):
        return f"Prestito {self._codice}: Strumento {self._id_strumento} affidato a {self._cognome_allievo} in data {self._data}"

    def __repr__(self):
        return f"Prestito('{self._codice}', '{self._data}', '{self._id_strumento}', '{self._cognome_allievo}')"


class DepositoStrumenti:
    def __init__(self, nome, responsabile):
        """Inizializza gli attributi e le strutture dati"""
        self.nome = nome
        self.responsabile = responsabile
        self.strumenti = {}  # Dizionario id_strumento -> Oggetto Strumento
        self.prestiti = {}  # Dizionario id_prestito -> Oggetto Prestito
        self.strumenti_in_prestito = set()  # Set di id_strumento attualmente in prestito

    def carica_file_strumenti(self, file_path):
        """Carica gli strumenti dal file"""
        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                # Gestisce sia file CSV standard sia righe senza separatore esplicito se formattate come nell'esempio base
                # Nel caso del formato "S1,Chitarra,...", utilizziamo il modulo csv standard.
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    # Se il file contiene righe appiccicate senza virgole multiple, gestiamo eventuali formati particolari,
                    # ma assumendo il formato CSV standard con virgole:
                    if len(row) >= 5:
                        codice = row[0].strip()
                        tipo = row[1].strip()
                        marca = row[2].strip()
                        anno_acquisto = int(row[3].strip())
                        valore = float(row[4].strip())

                        strumento = Strumento(codice, tipo, marca, anno_acquisto, valore)
                        self.strumenti[codice] = strumento
        except FileNotFoundError:
            raise FileNotFoundError(f"Errore: Il file '{file_path}' non è stato trovato.")
        except Exception as e:
            raise Exception(f"Errore durante la lettura del file: {e}")

    def aggiungi_strumento(self, tipo, marca, anno_acquisto, valore):
        """Aggiunge uno strumento nel deposito: aggiunge solo nel sistema e non aggiorna il file"""
        # Calcola il codice progressivo a partire dall'ultimo identificativo presente
        if self.strumenti:
            # Estrae il numero intero dall'ultimo id (es. "S12" -> 12)
            max_id = max(int(k[1:]) for k in self.strumenti.keys() if k.startswith('S') and k[1:].isdigit())
            nuovo_id_num = max_id + 1
        else:
            nuovo_id_num = 1

        nuovo_codice = f"S{nuovo_id_num}"
        strumento = Strumento(nuovo_codice, tipo, marca, anno_acquisto, valore)
        self.strumenti[nuovo_codice] = strumento
        return strumento

    def strumenti_ordinati_per_marca(self):
        """Ordina gli strumenti per marca in ordine alfabetico"""
        return sorted(self.strumenti.values(), key=attrgetter('marca'))

    def nuovo_prestito(self, data, id_strumento, cognome_allievo):
        """Crea un nuovo prestito"""
        id_strumento = id_strumento.strip()

        # Verifica se lo strumento esiste nel sistema
        if id_strumento not in self.strumenti:
            raise Exception(f"Errore: Lo strumento con ID '{id_strumento}' non esiste nel sistema.")

        # Verifica se lo strumento è già in prestito
        if id_strumento in self.strumenti_in_prestito:
            raise Exception(f"Errore: Lo strumento '{id_strumento}' è attualmente già in prestito.")

        # Calcola il codice progressivo del prestito
        if self.prestiti:
            max_p = max(int(k[1:]) for k in self.prestiti.keys() if k.startswith('P') and k[1:].isdigit())
            nuovo_p_num = max_p + 1
        else:
            nuovo_p_num = 1

        id_prestito = f"P{nuovo_p_num}"

        prestito = Prestito(id_prestito, data, id_strumento, cognome_allievo)
        self.prestiti[id_prestito] = prestito
        self.strumenti_in_prestito.add(id_strumento)

        return prestito

    def termina_prestito(self, id_prestito):
        """Termina un prestito in atto"""
        id_prestito = id_prestito.strip()

        if id_prestito not in self.prestiti:
            raise Exception(f"Errore: Il codice prestito '{id_prestito}' non corrisponde ad alcun prestito esistente.")

        prestito = self.prestiti.pop(id_prestito)
        # Rimuove lo strumento dal set di quelli in prestito per renderlo nuovamente disponibile
        if prestito.id_strumento in self.strumenti_in_prestito:
            self.strumenti_in_prestito.remove(prestito.id_strumento)
