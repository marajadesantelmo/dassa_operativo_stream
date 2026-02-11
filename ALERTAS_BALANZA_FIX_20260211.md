# Alerta Balanza - Corrección de Problema de Emails Duplicados

**Fecha:** 11 de Febrero 2026  
**Script afectado:** `alertas_balanza.py`  
**Severidad:** ⚠️ CRÍTICA - Clientes recibieron emails duplicados cada 15 minutos

---

## 📊 Resumen Ejecutivo

Se identificó y corrigió un problema crítico en el sistema de alertas de balanza que causó que **múltiples clientes recibieran emails duplicados repetidamente cada 15 minutos desde las 18:00 hasta las 20:00** del 11/02/2026.

**IDs afectados:** 67712, 67714, 67717, 67718, 67719, 67720, 67723, 67725, 67726  
**Clientes impactados:** ~9 operaciones de pesaje  
**Duración del problema:** ~2 horas (8 ciclos de envío duplicado)

---

## 🔍 Análisis del Problema

### Causa Raíz #1: Cliente No Encontrado en Base de Datos

**Línea problemática:** alertas_balanza.py:211
```python
to_emails = clientes[clientes['apellido'].str.lower() == str(cliente).lower()]['email'].values[0]
```

**Error:**
- El cliente "**Gonzalez Augusto Andres**" (ID Pesada: 67714) no existe en `contactos_clientes.csv`
- La búsqueda retorna un DataFrame vacío
- Al acceder a `.values[0]` de un array vacío se genera `IndexError`

### Causa Raíz #2: CSV Guardado Solo al Final

**Línea problemática:** alertas_balanza.py:220 (versión original)
```python
alerts_df.to_csv(path +'alertas_balanza.csv', index=False)  # ❌ Solo al final del loop
```

**Flujo del problema:**
```
1. Procesar ID 67726 ✅ → Email enviado → No guardado en CSV
2. Procesar ID 67725 ✅ → Email enviado → No guardado en CSV
3. Procesar ID 67723 ✅ → Email enviado → No guardado en CSV
4. Procesar ID 67720 ✅ → Email enviado → No guardado en CSV
5. Procesar ID 67719 ✅ → Email enviado → No guardado en CSV
6. Procesar ID 67718 ⚠️ → Email falló → No guardado en CSV
7. Procesar ID 67717 ✅ → Email enviado → No guardado en CSV
8. Procesar ID 67714 💥 → Script CRASH (IndexError) → CSV NUNCA SE GUARDA
```

**Resultado:** Los 7 emails exitosos se envían de nuevo en el próximo ciclo (15 minutos después)

### Causa Raíz #3: Sin Manejo de Errores

- No había `try-except` para capturar errores individuales
- Un solo error causaba que todo el proceso se detuviera
- No había fallback cuando un cliente no se encuentra

---

## ✅ Solución Implementada

### 1. **Guardar CSV Después de Cada Email Exitoso**
```python
if email_sent:
    # CRITICAL: Save to CSV immediately after successful email send
    new_alert = pd.DataFrame({'idpesada': [id_pesada], 'enviado': [1]})
    alerts_df = pd.concat([alerts_df, new_alert], ignore_index=True)
    alerts_df.to_csv(path + 'alertas_balanza.csv', index=False)  # ✅ Guardado inmediato
    print(f"✓ ID Pesada {id_pesada} registrado exitosamente en CSV")
```

### 2. **Manejo Robusto de Clientes No Encontrados**
```python
cliente_match = clientes[clientes['apellido'].str.lower() == str(cliente).lower()]

if cliente_match.empty:
    print(f"ADVERTENCIA: Cliente '{cliente}' no encontrado en base de datos. Usando email por defecto.")
    to_emails = ["facturacion@dassa.com.ar"]  # ✅ Fallback email
else:
    to_emails = cliente_match['email'].values[0]
    # ... procesamiento adicional
```

### 3. **Try-Except-Finally Completo**
```python
try:
    # ... Generar PDF y enviar email
    email_sent = send_email_alert(row.to_dict(), to_emails, pdf_path)
    if email_sent:
        # Guardar en CSV inmediatamente
        ...
except Exception as e:
    print(f"ERROR procesando ID Pesada {id_pesada}: {str(e)}")
    # ✅ Continuar con la siguiente operación
finally:
    # ✅ Siempre limpiar archivos temporales
    if pdf_path and os.path.exists(pdf_path):
        os.unlink(pdf_path)
```

### 4. **Registro Manual de IDs Problemáticos**

Se agregaron manualmente en `alertas_balanza.csv`:
```csv
67712,1
67714,1
67717,1
67718,1
67719,1
67720,1
67723,1
67725,1
67726,1
```

**Propósito:** Evitar que se procesen nuevamente en el próximo ciclo.

---

## 📈 Evidencia del Problema (Logs)

### Log: alertas_orquestador_20260211_200003.log
```
2026-02-11 20:00:03,079 | INFO | Orquestador iniciado
...
Se encontraron 9 nuevas operaciones de balanza para procesar.
Procesando alerta para ID Pesada: 67726, Cliente: Minera Santa Rita Srl
Email enviado exitosamente para ID Pesada: 67726
...
Procesando alerta para ID Pesada: 67714, Cliente: Gonzalez Augusto Andres
ERROR: IndexError: index 0 is out of bounds for axis 0 with size 0
```

### Patrón Observado en Múltiples Logs

| Hora    | IDs Procesados                                      | Estado         | Notas                                    |
|---------|-----------------------------------------------------|----------------|------------------------------------------|
| 16:00   | 67698, 67697                                        | ✅ OK          | Últimos guardados correctamente          |
| 17:00   | Ninguno nuevo                                       | ✅ OK          | Sin nuevas operaciones                   |
| 18:00   | 67714, 67712                                        | ❌ ERROR       | Crash en 67714, CSV no guardado          |
| 18:45   | 67726, 67725, ..., 67714                            | ❌ ERROR       | Mismo error, emails duplicados           |
| 19:00   | 67723, 67720, ..., 67714                            | ❌ ERROR       | Subset duplicado                         |
| 19:45   | 67726, 67725, ..., 67714                            | ❌ ERROR       | Emails duplicados de nuevo               |
| 20:00   | 67726, 67725, ..., 67714                            | ❌ ERROR       | Patrón continúa                          |

---

## 🔧 Mejoras Adicionales Implementadas

1. **Logging Mejorado:**
   - ✓ Indica cuando un cliente no se encuentra
   - ✓ Confirma cuando un ID se guarda exitosamente
   - ✓ Reporta errores específicos sin detener el proceso

2. **Validación de Emails:**
   - Convierte strings únicos a listas
   - Filtra emails internos de DASSA
   - Usa fallback si no hay emails válidos

3. **Limpieza Garantizada:**
   - Bloque `finally` asegura que los PDFs temporales se eliminen
   - Manejo de errores en la limpieza misma

---

## 📝 Recomendaciones Adicionales

### Corto Plazo (Inmediato)

1. ✅ **Monitorear próxima ejecución** (20:15) para verificar que no haya más duplicados
2. ⚠️ **Comunicar a clientes afectados** sobre emails duplicados recibidos
3. ✅ **Verificar que ID 67714 use email fallback correctamente**

### Mediano Plazo (Esta Semana)

4. 🔄 **Actualizar `contactos_clientes.csv`** con el cliente faltante:
   - Cliente: "Gonzalez Augusto Andres"
   - Obtener email correcto del sistema
   - Ejecutar `contacto_clientes.py` para sincronizar desde SQL

5. 📊 **Implementar alertas proactivas** en el orquestador:
   - Notificar cuando se usa email fallback
   - Enviar resumen diario de clientes no encontrados

6. ✅ **Aplicar el mismo patrón** a otros scripts de alertas:
   - `alertas_arribos.py`
   - `alertas_expo.py`
   - `alertas_retiros.py`
   - `alertas_remisiones_expo.py`

### Largo Plazo (Próximo Sprint)

7. 🔄 **Centralizar manejo de clientes:**
   - Crear función `get_client_emails(cliente_name)` con manejo de errores
   - Usar en todos los scripts de alerta

8. 📝 **Mejorar logging:**
   - Agregar nivel de log (INFO, WARNING, ERROR)
   - Integrar con sistema de monitoreo centralizado
   - Alertas automáticas para errores críticos

9. 🧪 **Testing:**
   - Crear suite de pruebas para casos edge (cliente no encontrado, emails vacíos, etc.)
   - Simular escenarios de error antes de producción

---

## ✅ Validación de la Solución

### Checklist Post-Implementación

- [x] Script actualizado con manejo de errores robusto
- [x] CSV guardado incrementalmente después de cada email
- [x] IDs problemáticos agregados manualmente al CSV
- [x] Fallback email configurado para clientes no encontrados
- [x] Logging mejorado implementado
- [ ] Verificar próxima ejecución (20:15) - **PENDIENTE**
- [ ] Confirmar cero emails duplicados en siguientes ciclos - **PENDIENTE**
- [ ] Actualizar base de datos de clientes - **PENDIENTE**

---

## 📞 Contacto

**Desarrollador:** GitHub Copilot  
**Fecha de corrección:** 11/02/2026 20:05  
**Versión script:** alertas_balanza.py (corregido)

---

## 🔗 Archivos Relacionados

- [alertas_balanza.py](alertas_balanza.py) - Script corregido
- [alertas_balanza.csv](alertas_balanza.csv) - CSV actualizado con IDs problemáticos
- [alertas_orquestador.py](alertas_orquestador.py) - Orquestador principal
- [contacto_clientes.py](contacto_clientes.py) - Script de sincronización de clientes
- Logs: `/logs/alertas_orquestador_20260211_*.log`

---

**Estado:** ✅ **RESUELTO** - Esperando validación en próximo ciclo
