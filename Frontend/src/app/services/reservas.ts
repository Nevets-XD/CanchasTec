import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface Cancha {
  id: number;
  nombre: string;
  tipo: string;
  capacidad: string;
  precio_hora: number;
  estado: string;
}

interface Reserva {
  id: number;
  usuario_id?: number;
  usuario_nombre?: string;
  usuario_email?: string;
  cancha_id: number;
  cancha_nombre: string;
  cancha_tipo: string;
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  estado: string;
  fecha_creacion: string;
}

@Injectable({
  providedIn: 'root'
})
export class ReservasService {
  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) {}

  // Obtener canchas disponibles
  getCanchas(): Observable<{ canchas: Cancha[] }> {
    return this.http.get<{ canchas: Cancha[] }>(`${this.apiUrl}/canchas`);
  }

  // Crear reserva (Cliente)
  crearReserva(reserva: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/reservas`, reserva);
  }

  // Obtener reservas de un usuario (Cliente)
  getReservasUsuario(usuarioId: number): Observable<{ reservas: Reserva[] }> {
    return this.http.get<{ reservas: Reserva[] }>(`${this.apiUrl}/reservas/usuario/${usuarioId}`);
  }

  // Obtener todas las reservas (Admin)
  getTodasReservas(): Observable<{ reservas: Reserva[] }> {
    return this.http.get<{ reservas: Reserva[] }>(`${this.apiUrl}/reservas`);
  }

  // Actualizar estado de reserva (Admin)
  actualizarEstadoReserva(reservaId: number, estado: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/reservas/${reservaId}/estado`, { estado });
  }
}