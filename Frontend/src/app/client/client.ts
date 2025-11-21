import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../services/auth';
import { ReservasService } from '../services/reservas';

@Component({
  selector: 'app-client',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './client.html',
  styleUrls: ['./client.css']
})
export class ClientComponent implements OnInit {
  currentUser: any = null;
  canchas: any[] = [];
  misReservas: any[] = [];
  mostrarFormReserva: boolean = false;
  
  // Datos del formulario
  canchaSeleccionada: number = 0;
  fecha: string = '';
  horaInicio: string = '';
  horaFin: string = '';
  mensajeError: string = '';
  mensajeExito: string = '';
  isLoading: boolean = false;

  constructor(
    private authService: AuthService,
    private reservasService: ReservasService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.currentUserValue;
    
    if (!this.currentUser || this.currentUser.tipo_usuario.toLowerCase() !== 'usuario') {
      alert('Acceso denegado.');
      this.router.navigate(['/']);
      return;
    }

    this.cargarCanchas();
    this.cargarMisReservas();
  }

  cargarCanchas(): void {
    this.reservasService.getCanchas().subscribe({
      next: (response) => {
        this.canchas = response.canchas;
        console.log('Canchas cargadas:', this.canchas);
      },
      error: (error) => {
        console.error('Error al cargar canchas:', error);
      }
    });
  }

  cargarMisReservas(): void {
    this.reservasService.getReservasUsuario(this.currentUser.id).subscribe({
      next: (response) => {
        this.misReservas = response.reservas;
        console.log('Reservas cargadas:', this.misReservas);
      },
      error: (error) => {
        console.error('Error al cargar reservas:', error);
      }
    });
  }

  mostrarFormulario(): void {
    this.mostrarFormReserva = true;
    this.mensajeError = '';
    this.mensajeExito = '';
  }

  ocultarFormulario(): void {
    this.mostrarFormReserva = false;
    this.limpiarFormulario();
  }

  limpiarFormulario(): void {
    this.canchaSeleccionada = 0;
    this.fecha = '';
    this.horaInicio = '';
    this.horaFin = '';
    this.mensajeError = '';
    this.mensajeExito = '';
  }

  crearReserva(): void {
    this.mensajeError = '';
    this.mensajeExito = '';

    // Validaciones
    if (!this.canchaSeleccionada || !this.fecha || !this.horaInicio || !this.horaFin) {
      this.mensajeError = 'Por favor completa todos los campos';
      return;
    }

    if (this.horaInicio >= this.horaFin) {
      this.mensajeError = 'La hora de fin debe ser posterior a la hora de inicio';
      return;
    }

    this.isLoading = true;

    const reserva = {
      usuario_id: this.currentUser.id,
      cancha_id: this.canchaSeleccionada,
      fecha: this.fecha,
      hora_inicio: this.horaInicio,
      hora_fin: this.horaFin
    };

    this.reservasService.crearReserva(reserva).subscribe({
      next: (response) => {
        console.log('Reserva creada:', response);
        this.mensajeExito = '¡Reserva creada exitosamente! Está pendiente de aprobación.';
        this.isLoading = false;
        this.limpiarFormulario();
        this.cargarMisReservas();
        
        setTimeout(() => {
          this.ocultarFormulario();
        }, 2000);
      },
      error: (error) => {
        console.error('Error al crear reserva:', error);
        this.isLoading = false;
        this.mensajeError = error.error?.message || 'Error al crear la reserva';
      }
    });
  }

  getEstadoClass(estado: string): string {
    switch(estado) {
      case 'aprobada': return 'badge bg-success';
      case 'pendiente': return 'badge bg-warning text-dark';
      case 'rechazada': return 'badge bg-danger';
      case 'cancelada': return 'badge bg-secondary';
      default: return 'badge bg-secondary';
    }
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/Login']);
  }
}