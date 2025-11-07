import express from "express";
import pool from "../db.js";

const router = express.Router();

router.post("/:usuarioId", async (req, res) => {
  const { usuarioId } = req.params;
  const maxIntentos = 3;
  let intento = 0;

  while (intento < maxIntentos) {
    try {
      await pool.query(
        "INSERT INTO boletos (usuario_id, asignado) VALUES ($1, TRUE)",
        [usuarioId]
      );
      return res.json({ mensaje: "Boleto asignado correctamente" });
    } catch (error) {
      intento++;
      console.log(`Intento ${intento} falló: ${error.message}`);
      if (intento >= maxIntentos) {
        return res.status(500).json({
          mensaje: "Error persistente: no se pudo asignar el boleto",
        });
      }
    }
  }
});

export default router;

