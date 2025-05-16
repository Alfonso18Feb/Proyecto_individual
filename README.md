# Proyecto_individual
# link: https://github.com/Alfonso18Feb/Proyecto_individual
**Para el proyecto individual he creado un periodico que manda problemas como sudokus y laberintos a sus subscriptores que le guesten dichos rompecabezas**
## Descripción del proyecto:
### Creamos un entorno con PUB/SUB donde el publicador seria los de la editorial y los subscriptores son personas que les gustan los rompe cabezas.
### Los editores de 20minutos utilizan una programacion distribuida para mandar todos los 50 laberintos y sudokus a sus subscriptores.
### Para ellos los editores pidieron a varias oficinas de generadores de rompecabezas que generen laberintos de 4x4 hasta 100x100. Tambien incluyando otras oficinas que se dedican a crear sudokus que varian de nivel (Facil, Normal, Medio). Luego las oficinas se comunican con la editorial que las mandara a nuestro sistema brocker que distrubuye todos los rompecabezas a los subscriptores.
##  Problemas que resuelve:
### Lo que resuelve es ya que hay muchas oficinas creando nuestros rompecabezas si una de ellas deja de funcionar no nos retrasaria nuestra publicacion de los problemas a nuestros subscriptores. Tambien como nos comunicamos, con colas, es muy eficiente ya que casi todos los 50 sudokus y laberintos se pueden enviar casi inmediatamente. Esto proporcionaria una gran satisfacion a nustros clientes. En otras palabras, resuelve el problema de generar laberintos y sudokus en paralelo y tambien nos proporciona un brocker que envia nustros rompecabezas de una manera segura.
## Como esta estructurado:
### Esta estructurado de la siguiente manera tenemos un codigo 20minutos que representa La editorial que crear los rompecabezas utilizando Depth for Search para generar los laberinto y luego generan los sudokus quitandoles varios numeros dependiendo de la dificultad. Luego despues los workers son como las oficinas que estan trabajando en paralelo generando los sudokus y laberintos. Despues, tenemos una cola que comunica los procesos, genreramos los laberintos (worker) y luego las oficinas de publicar laberintos las revisan y la envian al brocker. Despues de enviar los rompecabezas dejamos de publicar.
### Luego estan los Subscriptores donde en el Main podemos elegir si queremos subscribirnos a Laberinto o Sudoku. Cuando hayamos elegido la apcion. Nos comunicamos con el brocker y resolvemos los rompecabezas. Para resolver dichos problemas utilizamos DFS para encontrar la salida del laberinto. Utilizamos backtracking para resolver los sudokus. Estos suubscriptores estaran conectados y cuando salgan aparecera el tiempo total que tardaron en resolver los rompecabezas.
## Tecnicas de concurencia y pararelismo utilizas y porque.
### Utilizamos PUB/SUB con diferentes canales laberinto y sudoku utilizamos este metodo de programacion distrubuida ya que nos permite compartir los rompecabezas a varias personas de una forma segura y rapido utilizando el brocker RabbitMQ. Tambien utilizamos multiprocesos para generar y publicar laberintos esto es debido a que generar laberintos y sudokus y luego publicarlos sea muy lento asi que es mejor utilizar multiprocesos con una comunicacion de cola para generar y publicar rapidamente estos rompecabezas.

## Explicacion y visualizacion de como se ejecuta.
### Lo primero que debes hacer es entrar y ejecutar el codigo de subscriptor ya que si no hay subscriptores entonces los publicadores no pueden mandar ningun rompecabezas a nadie.
Luego debes insertar si quieres rompecabezas de laberinto o sudoku. Al escribir el comando te aparece lo que se puede observar en la primera foto si no escribes lo correcto te sale lo que aparece en la segunda foto
![image](https://github.com/user-attachments/assets/03bca2e0-fa00-42f7-9c7e-0c9b8df4d038)      ![image](https://github.com/user-attachments/assets/ea50bb2b-dc3c-4f5f-b633-ed6f2642fe24)

Puedes Abrir las terminales que quieras y subscribirte a una de las dos laberinto o sudoku como esta visto en el la siguiente foto (es recomendable solo dos)
![image](https://github.com/user-attachments/assets/689faa17-dedb-48a8-ae01-a820ffcb1738)

Luego si estas en la carpeta donde estan los dos codigos. Abre una nueva terminal y escribe python 20minutos.py para ejecutarla.
![image](https://github.com/user-attachments/assets/00e19eda-4012-4630-9fbc-15a521051260)

Finalmente, 20minutos publicara 50 laberintos y sudokus y RabbitMQ los ira mandando a los subscriptores que se hayan subscrito.

![image](https://github.com/user-attachments/assets/4612684d-c58d-478d-9b03-e89a2acb7bc6)
Como puedes ver en la foto de ariba aparece el tiempo que tardaron en resolverlo y tambien dificultad del sudoku o los pasos para llegar a la salida para el laberinto

Ademas, te devuelven la solucion con matplot en rojo.
![image](https://github.com/user-attachments/assets/4df6c32b-8b78-480e-a6c1-54835ee9a02d)  ![image](https://github.com/user-attachments/assets/6e5ca296-c783-47f8-a85d-ae7a78f3709c)

Si se pierde la conexion con los publicadores te devuelve un error para prevenir cualquier causa maligna ya que utilizamos programacion distribuida. Devolviendo tiempo total y promedio. Esto se puede tambien conseguir si en la terminal haces Ctrl+C
![image](https://github.com/user-attachments/assets/082223d8-37ed-46db-aa58-3d4ab6825d55)

