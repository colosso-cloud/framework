# Policy Layer - `src/application/policy`

Questa cartella contiene le **policy dichiarative** dell’applicazione, scritte in linguaggio [Rego](https://www.openpolicyagent.org/docs/latest/policy-language/), valutate tramite **Open Policy Agent (OPA)**.

---

## 🎯 Obiettivo

Le policy definiscono **chi può fare cosa, quando e su cosa**, in base al contesto applicativo.  
Consentono di separare la logica decisionale da quella esecutiva, rendendo trasparente e modificabile il comportamento autorizzativo dell’applicazione.

---

## 📁 Organizzazione

Le policy sono organizzate in sottocartelle tematiche, in base all’ambito che regolano:

### Criteri di organizzazione

| Cartella            | Quando usarla                                                                 |
|---------------------|-------------------------------------------------------------------------------|
| `authentication/`   | Per regolare accessi, ruoli, token, login/logout                             |
| `presentation/`     | Per decidere cosa mostrare o nascondere in base al ruolo o al contesto       |
| `repository/`       | Per operazioni su repo: lettura, aggiornamento, creazione, struttura         |

---

## 🧠 Linguaggio: Rego

Le policy sono scritte in **Rego**, linguaggio dichiarativo utilizzato da OPA.

### Esempio `repository.rego`
```rego
package application.policy.repository

default allow = false

allow {
  input.action == "view"
  input.subject.role == "reader"
}

allow {
  input.action == "update"
  input.subject.role == "admin"
}

deny_reason[msg] {
  not allow
  msg := "Accesso negato: ruolo non autorizzato"
}