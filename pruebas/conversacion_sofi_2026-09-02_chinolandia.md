# Prueba de conversación — Sofi / Chinolandia SV (con catálogo)

- **Fecha:** 2026-09-02
- **Tienda:** Chinolandia SV (detectada / por defecto)
- **Producto en catálogo:** Lápiz de acupuntura sin agujas — $24.75
- **Modo:** local (`pruebas/prueba_sofi.py`), sin pasar por WhatsApp
- **Modelo:** claude-sonnet-5
- **Costo aprox.:** US$0.03

---

### [1] Cliente
> Hola, vi en un anuncio de Facebook el lápiz de acupuntura, cuanto cuesta?

### Sofi
> ¡Hola! Soy Sofi, asesora de ventas de Chinolandia SV 😊
>
> Sí, es el lápiz de acupuntura sin agujas, cuesta $24.75 y ya incluye el envío GRATIS a todo El Salvador.
>
> Es un lápiz de electroestimulación que aplica microcorrientes en puntos de acupuntura, sin usar agujas. Tiene 9 niveles de intensidad, es portátil y viene con 2 puntas intercambiables más 2 geles conductores. Sirve bastante para dolores musculares y articulares, contracturas, ciática, tensión de espalda y cuello.
>
> ¿Te gustaría pedirlo o tenés alguna duda antes?

---

### [2] Cliente
> Y cuantos niveles tiene? que trae en la caja?

### Sofi
> Tiene 9 niveles de intensidad, para que puedas ir subiendo poco a poco según lo que se te haga más cómodo.
>
> Y en la caja viene: el lápiz de acupuntura, 2 puntas intercambiables y 2 geles conductores para usarlo.
>
> ¿Te animás a pedirlo? 😊

---

### [3] Cliente
> Perfecto. Quiero pedir uno

### Sofi
> ¡Excelente! Vamos con tu pedido entonces.
>
> Pasame estos datos, uno por uno o todos juntos, como prefieras:
>
> Nombre completo
> Número de teléfono de contacto
> Dirección completa de entrega
> Punto de referencia (si tenés)
> Forma de pago: contra entrega, transferencia o enlace de pago

---

### [4] Cliente
> Carlos Menjivar, 7788-1234, Colonia Escalon calle 5 casa 12, San Salvador. Pago contra entrega

### Sofi
> Perfecto, Carlos, ya tengo todo. Te resumo el pedido:
>
> Producto: Lápiz de acupuntura sin agujas x1 - $24.75 (envío gratis)
> Nombre: Carlos Menjivar
> Teléfono: 7788-1234
> Dirección: Colonia Escalón, calle 5, casa 12, San Salvador
> Forma de pago: contra entrega
>
> ¿Me confirmás que todo está correcto para dejarlo listo? 😊

---

### [5] Cliente
> Cuanto tarda en llegar? el envio tiene costo?

### Sofi
> El envío es gratis, no tiene ningún costo.
>
> Y el lápiz de acupuntura se entrega en 12 a 24 horas, así que lo tenés rapidito.
>
> ¿Confirmamos el pedido entonces, Carlos?

---

### [6] Cliente
> Y si no me funciona lo puedo devolver?

### Sofi
> Te cuento con toda sinceridad: no manejamos devoluciones por cambio de opinión o si sentís que no te funcionó. Solo se hacen cambios si el producto viene con algún desperfecto de fábrica, y eso hay que reportarlo dentro de los primeros 3 días desde que lo recibís, con su empaque original y sin uso.
>
> De igual forma, es un producto que a muchos clientes les ha dado buenos resultados para el alivio de dolores musculares y articulares. ¿Confirmamos tu pedido, Carlos? 😊

---

## Qué cambió respecto a la prueba anterior

- Sofi se presenta como **asesora de Chinolandia SV** (no "Oriental Group").
- **Da el precio y las especificaciones directo** desde el catálogo de la tienda,
  ya no manda todo a un asesor.
- El resumen del pedido incluye el producto con su precio.
- Envío y devoluciones correctos y específicos de este producto.

## Cómo funciona la detección de tienda (Opción B)

- Número de WhatsApp compartido para todo Oriental Group.
- El primer mensaje que llega desde un anuncio trae el objeto `referral` de Meta.
- `agent/tiendas.py` lo compara contra `deteccion.ad_ids` / `palabras_clave` /
  `fuentes_url` de cada tienda (`config/tiendas/<id>.yaml`).
- La tienda detectada se fija en la base para esa conversación; los mensajes
  siguientes (que ya no traen `referral`) la recuperan de ahí.
- Si no se detecta nada, se usa `agente.tienda_por_defecto` de `config/business.yaml`.

## Pendiente de que confirmes

1. **Precio $24.75**: ¿es único? ¿hay precio normal más alto o descuento por 2+?
2. **"¿Con qué pilas / cómo se carga?"**: dato faltante en el catálogo.
3. Cualquier ajuste de tono.

## Agregar más productos / tiendas

- Producto nuevo a Chinolandia SV → editar `knowledge/chinolandia-sv/catalogo.md`.
- Tienda nueva → crear `config/tiendas/<id>.yaml` + `knowledge/<id>/catalogo.md`,
  y sumar el `<id>` a la lista `tiendas:` de `config/business.yaml`.
