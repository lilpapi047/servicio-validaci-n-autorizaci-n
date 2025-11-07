import express from "express";
import dotenv from "dotenv";
import eligibilidadRouter from "./routes/eligibilidad.js";
import asignacionRouter from "./routes/asignacion.js"; 

dotenv.config();

const app = express();
app.use(express.json());

app.use("/verificar-eligibilidad", eligibilidadRouter);
app.use("/asignar-rifa", asignacionRouter);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en puerto ${PORT}`);
});
