# Prueba de conversación — Sofi (Oriental Group)

- **Fecha:** 2026-09-01
- **Modo:** local (`test_local.py` / script `prueba_sofi.py`), sin pasar por WhatsApp
- **Modelo:** claude-sonnet-5
- **Costo aprox.:** US$0.02–0.03 de saldo de Anthropic
- **Guion:** 6 mensajes simulando un cliente que llega desde un anuncio

---

### [1] Cliente
> Hola, vi en un anuncio de Facebook el masajeador de cuello, cuanto cuesta?

### Sofi
> ¡Hola! Qué bueno que nos escribas 😊 Con gusto te ayudo con el masajeador de cuello.
>
> Para no darte un dato equivocado, déjame confirmar el precio con un asesor.
>
> ¿Me compartes tu nombre para que te contacten con esa info? Mientras tanto, contame, ¿es para vos o para regalar?

---

### [2] Cliente
> Me llamo Carlos Menjivar

### Sofi
> Mucho gusto, Carlos 😊 Ya te dejo anotado para que un asesor te confirme el precio del masajeador de cuello.
>
> ¿Me regalas también tu número de teléfono para que te contacten más rápido? Y contame, ¿es para uso personal o para regalo?

---

### [3] Cliente
> Ok. Mejor quiero pedir las luces LED para mi carro, un juego. Es para un Toyota Corolla 2015

### Sofi
> ¡Perfecto, Carlos! Anoto tu pedido: un juego de luces LED para tu Toyota Corolla 2015.
>
> Ahora necesito unos datos para el envío:
> ¿Me confirmas tu número de teléfono de contacto?
> ¿Y tu dirección completa de entrega, con algún punto de referencia si tienes?

---

### [4] Cliente
> Carlos Menjivar, 7788-1234, Colonia Escalon calle 5 casa 12, San Salvador. Pago contra entrega

### Sofi
> ¡Gracias, Carlos! Ya tengo todos tus datos. Te dejo el resumen de tu pedido:
>
> Producto: 1 juego de luces LED para Toyota Corolla 2015
> Nombre: Carlos Menjivar
> Teléfono: 7788-1234
> Dirección: Colonia Escalón, calle 5, casa 12, San Salvador
> Forma de pago: Contra entrega
>
> ¿Todo correcto para confirmarlo así? 😊

---

### [5] Cliente
> Perfecto. Y el envio tiene costo? cuanto tarda?

### Sofi
> ¡No te preocupes, el envío es totalmente gratis! 🚚
> Y normalmente el pedido llega entre 12 y 48 horas, dependiendo de tu zona. Antes de la entrega te va a contactar el repartidor para coordinar todo.
>
> Con eso, ¿confirmamos tu pedido tal como te lo compartí?

---

### [6] Cliente
> Una ultima cosa, si no me gusta lo puedo devolver?

### Sofi
> Con gusto te cuento, Carlos: no manejamos devoluciones. Solo hacemos cambios si el producto tiene algún desperfecto de fábrica, reportándolo dentro de los primeros 3 días desde la entrega, con el empaque original y sin uso.
>
> Fuera de eso, no hay devolución. ¿Con esa info seguimos confirmando tu pedido? 😊

---

## Evaluación

| Qué se probó | Resultado |
|---|---|
| Pregunta de precio desde anuncio | OK — no inventó precio, ofreció asesor y pidió nombre |
| Tono cercano y amable | OK — cálida, usa el nombre, 1 emoji por mensaje |
| Tomar el pedido | OK — recolectó producto, nombre, teléfono, dirección y pago; resumen + confirmación |
| Info de envío | OK — gratis, 12–48 h, repartidor coordina (coincide con las FAQ) |
| Política de devolución | OK — exacta según el documento |
| Estilo WhatsApp | OK — mensajes cortos, sin markdown, cierra con pregunta |

### Ajustes posibles (opcionales)
- Mezcla "vos" y "tú" (natural para El Salvador; se puede fijar a uno solo).
- Insiste bastante en "¿es para vos o para regalar?"; se puede suavizar.

## Cómo repetir esta prueba
```
cd "C:\Users\User\Documents\AGENTE DE WHATSSAP\whatsapp-agentkit"
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" pruebas\prueba_sofi.py
```
O el chat interactivo (escribes tú los mensajes):
```
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" tests\test_local.py
```
