from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from markov import generate_text_hist
from cifrado_cesar import cifrado_cesar
from rrlnhcc import sol_rrlnhcc
import simbolico as sim


global gen_text
global hist
gen_text = ""
hist = None
TOKEN = "6434936644:AAGX-mGnmAhgYa_wtU4WJ4IvsBZceWSw2Gc"

async def start_command(update, context): 
    """Función correspondiente al comando /start"""
    await update.message.reply_text(
        "¡Bienvenido querido usuario!\n este es tu bot 'cucharadita diaria'. Escribe /ayuda para ver los comandos."
    )

async def ayuda_command(update, context):
    """Función correspondiente al comando /ayuda"""
    await update.message.reply_text(
        "Bienvenido al Bot de Asistencia 'cucharadita diaria'. Aquí tienes algunos comandos que puedes usar:\n"
        +"/start - Mensaje de bienvenida.\n"
        +"Elige algunas de las funciones que quieres usar de nuestro bot:\n"
        +"/cifrado - Permite cifrar o descifrar un mensaje de acuerdo al cifrado césar.\n"
        +"/markov - Permite generar textos con cadenas de Markov partiendo de una URL.\n"
        +"/rrlnhcc - Resuelve una recurrencia lineal no homogénea con coeficientes constantes.\n"
        +"/simbolico - Resuelve un problema por método simbólico."
    )
    
async def cifrado_command(update, context): 
    """Función correspondiente al comando /cifrado"""
    
    # arg contendrá las palabras que el usuario haya enviado después del comando /cifrado
    arg = context.args
    
    # Extrae mensaje a cifrar/descifrar
    try:
        msj = arg[arg.index("m:")+1:]
    except:
        msj = None
    
    # Extrae desplazamiento
    try:
        desp = " ".join(arg[arg.index("d:")+1:])
        if msj:
            msj = msj[:msj.index("d:")]
    except:
        desp = "0"
    
    if msj != None:
        msj = " ".join(msj)
    
    if msj != None:
        try:
            # Si desp no cumple el formato, se notifica al usuario del error
            if not desp.isdigit() or (desp == "0" and arg[0] == "cif"):
                raise Exception("'desp' debe ser un número entero positivo.")
            
            # Se realiza el cifrado/descifrado del msj
            if arg[0] == "cif":
                res, desp = cifrado_cesar(msj, int(desp), True)
            elif arg[0] == "des":
                res, desp = cifrado_cesar(msj, int(desp), False)
            else:
                # Si el argumento no está dentro de las opciones, se notifica al usuario
                raise Exception("Debe indicar 'des' para descifrar o 'cif' para cifrar.")
            
            if desp == 73:
                await update.message.reply_text(
                    "No se encontró un desplazamiento que generara una oración con sentido."
                )
            # Se envía al usuario el mensaje resultante y el desplazamiento usado
            await update.message.reply_text(
                f"Su mensaje cifrado con desplazamiento {desp}:\n{res}"
            )
        except Exception as e:
            # Si ocurre algún error, se indica al usuario qué ocurrió
            await update.message.reply_text(
                "Cometió un error escribiendo el comando. Revise: "+str(e)
            )
    else:
        # En cualquier otro caso, se le indica al usuario cómo usar el comando
        await update.message.reply_text(
            "Para cifrar un mensaje, escriba '/cifrado cif m: msj d: desp'.\n"
            +"Para descifrar, escriba '/cifrado des m: msj d: desp'.\n"
            +"Reemplace 'msj' por el mensaje que desea cifrar/descifrar "
            +"y 'desp' por el desplazamiento a aplicar según el cifrado "
            +"césar. El desplazamiento es opcional, pero solo para descifrar; "
            +"si no se ingresa o se ingresa '0', se tratará de buscar el mejor "
            +"desplazamiento."
        )
        
async def markov_command(update, context): 
    """Función correspondiente al comando /markov"""
    global gen_text
    global hist
    # arg contendrá las palabras que el usuario haya enviado después del comando /markov
    arg = context.args
    
    if gen_text == "" and len(arg) != 3:
        # Si no hay texto generado, y el usuario no dio indicaciones para generarlo,
        # se le indica cómo funciona el comando
        await update.message.reply_text(
            "No se ha generado ningún texto con cadenas de Markov aún.\n"
            +"Para la creación de un texto ficticio con cadenas de Markov, "
            +"debe ingresar junto al comando /markov: \n"
            +"- URL de un sitio web.\n"
            +"- El grado del modelo, K.\n"
            +"- El número de caracteres del texto resultante, N.\n"
            +"Escriba '/markov URL K N' para generar su texto.\n"
            +"Cuando ingrese el link, debe presionar la x para que no "
            +"envíe la previsualización."
        )
    elif len(arg) > 0:
        # Si el usuario ingreso alguna palabra tras el comando /markov, se verifican
        # para ejecutar las funciones de generar texto, mostrar histograma o mostrar texto
        if len(arg) == 3:
            # Si hay 3 palabras se asumen que son url, K, N y se trata de generar el texto
            try:
                # El texto se almacena en la variable global gen_text
                gen_text = generate_text_hist(arg[0], arg[1], arg[2])
                # Se notifica al usuario de la generación exitosa del texto
                await update.message.reply_text("Su texto ficticio ha sido creado.")
            except Exception as e:
                # Si ocurre algún error, se indica al usuario qué ocurrió
                await update.message.reply_text(str(e))
        elif arg[0] == "hist":
            await context.bot.send_photo(chat_id=update.message.chat_id, photo=r"hist.png")
        elif arg[0] == "texto":
            # Se escribe al usuario el texto anteriormente generado almacenado en gen_text
            await update.message.reply_text(gen_text)
    
    #if gen_text != "" and (len(arg) == 0 or (len(arg) > 0 and not arg[1] in ["hist", "texto"])):
    if gen_text != "":
        if len(arg) > 0:
            if arg[1] in ["hist", "texto"]:
                return
            
        # Si ya fue generado texto anteriormente y el usuario no invocó las funciones
        # de mostrar histograma o texto, se le informa acerca de estas funciones
        await update.message.reply_text(
            "Se ha generado un texto ficticio con la URL dada.\n"
            +"Si desea visualizar el texto, escriba '/markov texto'.\n"
            +"Si desea visualizar el histograma de frecuencias de las "
            +"K-tuplas, escriba '/markov hist'.\n"
            +"Si desea generar un nuevo texto o cambiar los parámetros, "
            +"escriba '/markov URL K N' para generar su texto."
        )

async def rrlnhcc_command(update, context):
    args = context.args
    
    # Si el usuario no escribe argumentos, se le indica cómo usar el comando
    if not args:
        await update.message.reply_text(
            "Para resolver una recurrencia lineal no homogénea con coeficientes constantes, "
            "necesitas proporcionar la función recurrente y las condiciones iniciales.\n\n"
            "Usa el comando de la siguiente manera:\n"
            "/rrlnhcc f(n)=a*f(n-1)+b*f(n-2)+...,f(0)=c,f(1)=d,...\n\n"
            "Por ejemplo:\n"
            "/rrlnhcc f(n)=2*f(n-1)+3*f(n-2),f(0)=1,f(1)=2",
            parse_mode="Markdown"
        )
        return

    input_str = " ".join(args)
    try:
        # Se ejecuta la función sol_rrlnhcc de la entrega 1 sobre los argumentos dados
        result_str, result_values = sol_rrlnhcc(input_str)
        # Se responde al usuario con la expresión y los valores respuesta
        await update.message.reply_text(result_str)
        for value in result_values:
            await update.message.reply_text(value)
    except Exception as e:
        # Si ocurre algun error se le notifica al usuario
        await update.message.reply_text(
            f"Error al procesar la recurrencia: {e}\n\n"
            "Asegúrate de que la función y las condiciones iniciales estén escritas correctamente."
        )

async def simbolico_callback(update, context):
    """Función auxiliar para comando /simbolico. Se ejecuta tras desplegarse el InlineKeyboard."""
    
    # Se obtienen n y la opción desde el CallbackQuery del botón presionado
    n, opc = update.callback_query.data.split(" ")
    await update.callback_query.answer()
    
    n = int(n)
    opc = int(opc)
    datos = [(2,"10"), (2,["010"]), (3,["12"]), (3,"012"), "", "", (5,["01","43"])]
    
    # Se ejecutan las funciones de acuerdo a la opción escogida
    if opc in [2, 3, 7]:
        r = sim.cad_sin_restr(n, datos[opc-1][0], datos[opc-1][1])
    elif opc in [1, 4]:
        r = sim.cad_con_subcad(n, datos[opc-1][0], datos[opc-1][1])
    elif opc == 5:
        r = sim.cad_par_unos(n)
    elif opc == 6:
        r = sim.cad_crecientes(n)
    # Se responde al usuario con el resultado
    await update.callback_query.message.reply_text(
        f"Las cadenas generadas para la opción {opc} son:\n"
        +f"{r}\n({len(r)} cadenas resultantes)"
    )
    
async def simbolico_command(update, context):
    """Función correspondiente al comando /simbolico"""
    args = context.args
    
    if len(args) != 1:
        await update.message.reply_text(
            "Para ver la solución de un problema por método simbólico, debe indicar el "
            +"valor de n, un entero no negativo, escribiendo '/simbolico n'."
        )
    elif not args[0].isdigit():
        await update.message.reply_text(
            "n debe ser un entero no negativo. Intente de nuevo."
        )
    else:
        if len(args) == 1:
            keyboard = [[]]
            for i in range(1, 8):
                keyboard[0].append(InlineKeyboardButton(str(i), callback_data=f"{args[0]} {i}"))

            await update.message.reply_text(
                "Opciones disponibles:\n"
                +"- Cadenas Binarias, de longitud n, que:\n  1. Contengan la subcadena '10'\n  2. Que No contengan '010'\n"
                +"- Cadenas Ternarias, de longitud n, que:\n  3. No contengan la subcadena '12'\n  4. Que contengan la subcadena '012'\n  5. Que contengan un número par de unos\n"
                +"- Cadenas númericas, de longitud n, de base cinco que:\n  6. Tengan sus caracteres en orden creciente.\n  7. Que No contengan las subcadenas '01' ni '43'\n",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

async def error(update, context): 
    print(f"Update {update} caused error {context.error}")

def main():
    print("Iniciando bot...")
    # Construye el bot
    app = Application.builder().token(TOKEN).build()
    # Añade comandos
    app.add_handler(CommandHandler("start", start_command)) 
    app.add_handler(CommandHandler("ayuda", ayuda_command)) 
    app.add_handler(CommandHandler("cifrado", cifrado_command)) 
    app.add_handler(CommandHandler("markov", markov_command))
    app.add_handler(CommandHandler("rrlnhcc", rrlnhcc_command))
    app.add_handler(CommandHandler("simbolico", simbolico_command))
    app.add_handler(CallbackQueryHandler(simbolico_callback))
    # Manejo de errores
    app.add_error_handler(error)
    # Run the bot until the user presses Ctrl-C
    app.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
    main()
