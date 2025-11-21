import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../services/auth';
import { ReservasService } from '../services/reservas';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin.html',
  styleUrls: ['./admin.css'],
})
export class AdminComponent implements OnInit {
  currentUser: any = null;
  todasReservas: any[] = [];
  mostrarReservas: boolean = false;
  isLoading: boolean = false;

  constructor(
    private authService: AuthService,
    private reservasService: ReservasService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.currentUserValue;

    if (!this.currentUser || this.currentUser.tipo_usuario.toLowerCase() !== 'administrador') {
      alert('Acceso denegado. Solo administradores.');
      this.router.navigate(['/']);
    }
  }

  verReservas(): void {
    this.mostrarReservas = true;
    this.cargarTodasReservas();
  }

  cargarTodasReservas(): void {
    this.isLoading = true;
    this.reservasService.getTodasReservas().subscribe({
      next: (response) => {
        this.todasReservas = response.reservas;
        this.isLoading = false;
        console.log('Reservas cargadas:', this.todasReservas);
      },
      error: (error) => {
        console.error('Error al cargar reservas:', error);
        this.isLoading = false;
      },
    });
  }

  aprobarReserva(reservaId: number): void {
    if (!confirm('¿Estás seguro de aprobar esta reserva?')) {
      return;
    }

    this.reservasService.actualizarEstadoReserva(reservaId, 'aprobada').subscribe({
      next: (response) => {
        console.log('Reserva aprobada:', response);
        alert('Reserva aprobada exitosamente');
        this.cargarTodasReservas();
      },
      error: (error) => {
        console.error('Error al aprobar reserva:', error);
        alert('Error al aprobar la reserva');
      },
    });
  }

  rechazarReserva(reservaId: number): void {
    if (!confirm('¿Estás seguro de rechazar esta reserva?')) {
      return;
    }

    this.reservasService.actualizarEstadoReserva(reservaId, 'rechazada').subscribe({
      next: (response) => {
        console.log('Reserva rechazada:', response);
        alert('Reserva rechazada');
        this.cargarTodasReservas();
      },
      error: (error) => {
        console.error('Error al rechazar reserva:', error);
        alert('Error al rechazar la reserva');
      },
    });
  }

  getEstadoClass(estado: string): string {
    switch (estado) {
      case 'aprobada':
        return 'badge bg-success';
      case 'pendiente':
        return 'badge bg-warning text-dark';
      case 'rechazada':
        return 'badge bg-danger';
      case 'cancelada':
        return 'badge bg-secondary';
      default:
        return 'badge bg-secondary';
    }
  }

  ocultarReservas(): void {
    this.mostrarReservas = false;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/Login']);
  }
}
