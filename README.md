# Account Payment Order - Pichincha EC Export

Módulo para Odoo 17 que agrega exportación de órdenes de pago en formato Banco Pichincha (Ecuador), usando archivo de texto delimitado por TAB.

## Funcionalidad

- Agrega el método de pago `ec_pichincha_tab` para órdenes de pago salientes.
- Permite generar archivo de pago desde la orden (`Generar archivo de pago`).
- Exporta cada pago con el formato solicitado por Banco Pichincha.
- Completa automáticamente la cuenta bancaria beneficiaria desde el partner cuando falta en la línea.
- Permite definir el tipo de cuenta de transferencia por cada banco del partner (`AHO/CTE/VIR`).

## Formato exportado

Columnas (en este orden):

1. `tipo`
2. `referencia`
3. `moneda`
4. `valor`
5. `CTA`
6. `tipo de cuenta`
7. `numero de cuenta`
8. `descripcion`
9. `tipo de identificacion`
10. `numero de identificacion`
11. `nombre`
12. `codigo ecuatoriano de banco`

Reglas:

- Delimitador: `TAB` (`\t`).
- Moneda por defecto: `USD`.
- Tipo por defecto: `PA`.
- Forma de pago (`CTA`) por defecto: `CTA`.
- Valor: sin punto decimal, en centavos (`20.30` => `2030`).
- `numero de cuenta`: se usa la cuenta bancaria del proveedor/beneficiario (`res.partner.bank`).
- `descripcion`: se toma de la cabecera de la orden de pago (`description`).
- `referencia`: prioriza la comunicación de las líneas de pago vinculadas al pago.

## Mapeos

### Tipo de identificación

- `C` = Cédula
- `R` = RUC
- `P` = Pasaporte

### Tipo de cuenta

- `AHO` = Ahorro
- `CTE` = Corriente
- `VIR` = Virtual

Prioridad de obtención del tipo de cuenta al exportar:

1. Campo `Tipo de Cuenta Transferencia` en la cuenta bancaria del partner.
2. `acc_type` de la cuenta bancaria (si está disponible).
3. Tipo por defecto del modo de pago Pichincha.

## Configuración

En **Modo de pago** (`account.payment.mode`), para método `ec_pichincha_tab`:

- Tipo de archivo (`PA`) editable.
- Moneda (`USD`) editable.
- Forma de pago (`CTA`) editable.
- Tipo de cuenta por defecto (`AHO/CTE/VIR`).
- Opción para incluir encabezado en el archivo.

## Comunicación en línea de pago

Para líneas de pago provenientes de facturas, el campo `comunicación` se completa con esta prioridad:

1. `l10n_latam_document_number`
2. `name`
3. `ref`
4. `payment_reference`

Esto aplica al crear líneas y también al confirmar la orden (si está en borrador).

## Dependencias

- `account_payment_order`
- `l10n_ec_bank_code_compat`

## Estado del botón "Fichero subido satisfactoriamente"

El botón no sube archivo al banco automáticamente.

Su función es:

- Publicar pagos.
- Reconciliar partidas contables internas.
- Cambiar estado a `uploaded`.

## Licencia

Este módulo se distribuye bajo licencia **AGPL-3**.
Ver archivo [LICENSE](./LICENSE).
