# Prueba — Sofi humanizada + descuento por cantidad

- **Fecha:** 2026-09-02
- **Tienda:** Chinolandia SV
- **Escenario:** cliente que llega por el dolor de su mamá y termina comprando 4 unidades
- **Objetivo:** validar (1) trato humano/empatía, (2) dato de batería, (3) descuento 10% desde 4 artículos
- **Modelo:** claude-sonnet-5 · **Costo aprox.:** US$0.04

---

### [1] Cliente
> Hola, vi el anuncio del lápiz de acupuntura. Mi mamá sufre mucho de dolor de rodillas y ya no sabe qué hacer

### Sofi
> Hola Carlos, soy Sofi, asesora de ventas de Chinolandia SV.
>
> Uy, qué duro ver a mamá sufriendo así con las rodillas, de verdad. Muchas personas usan el lápiz justo para ese tipo de molestias, dolor articular y muscular en general, aplicando microcorrientes en los puntos de dolor sin usar agujas, así que no le va a doler, más bien va a sentir un hormigueo suave que una empieza en el nivel más bajo y sube según lo tolere.
>
> Eso sí, para condiciones de rodilla puntuales siempre es bueno que lo consulte con su doctor también, pero como alivio para esas molestias del día a día muchos lo usan con buenos resultados.
>
> El lápiz cuesta $24.75, envío gratis a toda El Salvador, y llega en 12 a 24 horas. Trae 2 puntas, 2 geles y su batería incluida, listo para usar.
>
> ¿Querés que te lo mande a vos o directo a la casa de tu mamá?

---

### [2] Cliente
> Y con qué funciona? hay que estar comprando pilas?

### Sofi
> No, tranquilo, funciona con una sola batería doble A (AA) y esa ya viene incluida en la compra, así que no tenés que andar comprando nada aparte, llega listo para usar.
>
> ¿Te animás a pedirlo, Carlos? Si querés te tomo el pedido de una vez.

---

### [3] Cliente
> Está bien. Quiero llevar 4, uno para cada uno de mis hermanos también

### Sofi
> ¡Qué lindo detalle para tus hermanos! Y de una vez te cuento, por llevar 4 te aplica un 10% de descuento sobre el total, así que en vez de $99.00 quedaría en $89.10 por los 4 lápices.
>
> Para armarte el pedido necesito:
> Nombre completo (¿o son todos a tu nombre?)
> Número de teléfono de contacto
> Dirección completa de entrega
> Punto de referencia si tenés
> Forma de pago: contra entrega, transferencia o enlace de pago
>
> ¿Me vas pasando esos datos?

---

### [4] Cliente
> Sí, dale. Carlos Menjivar, 7788-1234, Colonia Escalón calle 5 casa 12, San Salvador, referencia frente a la tienda La Bendición. Pago contra entrega

### Sofi
> Perfecto Carlos, ya tengo todo. Te dejo el resumen:
>
> Pedido: 4 Lápices de acupuntura sin agujas
> Nombre: Carlos Menjivar
> Teléfono: 7788-1234
> Dirección: Colonia Escalón, calle 5, casa 12, San Salvador
> Referencia: frente a la tienda La Bendición
> Pago: contra entrega
>
> Precio: $24.75 c/u
> Subtotal: $99.00
> Descuento 10%: -$9.90
> Total a pagar: $89.10
> Envío: GRATIS
>
> ¿Todo correcto para confirmarte el pedido?

---

### [5] Cliente
> Perfecto, confirmado

### Sofi
> ¡Buenísimo Carlos! Ya queda tu pedido confirmado. Lo recibirás en 12 a 24 horas en la dirección que me diste, y pagás contra entrega los $89.10.
>
> Gracias por la compra, y ojalá tu mamá y tus hermanos sientan bien el alivio. Cualquier cosa que necesités, aquí estoy 😊

---

## Chequeo

| Requisito | Resultado |
|---|---|
| Trato humano, empatía real antes de vender | OK — reconoce el dolor de la mamá, "qué lindo detalle para tus hermanos" |
| No da consejo médico | OK — sugiere consultar al doctor para la rodilla |
| Dato de batería | OK — 1 batería AA incluida, "no tenés que comprar nada aparte" |
| Descuento 10% desde 4 artículos | OK — $99.00 → $89.10, desglosado en el resumen |
| 1 a 3 artículos: sin descuento | OK (no lo menciona hasta que pide 4) |
| Estilo WhatsApp, 1 emoji, sin script | OK — frases variadas, cierre cálido |

## Reglas nuevas aplicadas
- `config/business.yaml` → `defaults.descuento_cantidad` (10% desde 4 artículos)
- `knowledge/chinolandia-sv/catalogo.md` → batería AA incluida
- `config/prompts.yaml` → sección "Cómo hablás — lo más humana posible" + manejo del descuento en el pedido
