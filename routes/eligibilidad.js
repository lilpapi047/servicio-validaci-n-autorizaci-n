import express from "express";
import pool from "../db.js";

const router = express.Router();

router.get("/:usuarioId", async (req, res) => {
  const { usuarioId } = req.params;
  try {
    const result = await pool.query(
      "SELECT elegible FROM usuarios WHERE id = $1",
      [usuarioId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ mensaje: "Usuario no encontrado" });
    }

    res.json({ elegible: result.rows[0].elegible });
  } catch (error) {
    console.error(error);
    res.status(500).json({ mensaje: "Error al verificar elegibilidad" });
  }
});

export default router;
