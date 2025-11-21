import { Routes } from '@angular/router';
import { Home } from './home/home';
import { Creators } from './creators/creators';
import { LoginComponent } from './login/login';
import { RegisterComponent } from './register/register';
import { AdminComponent } from './admin/admin';
import { ClientComponent } from './client/client';

export const routes: Routes = [
  { path: '', component: Home }, // ruta principal
  { path: 'creators', component: Creators },
  { path: 'Login', component: LoginComponent },
  { path: 'Register', component: RegisterComponent },
  
  
  // Nuevas rutas para admin y cliente
  { path: 'admin', component: AdminComponent },
  { path: 'client', component: ClientComponent },
  
  // Redirección para rutas no encontradas
  { path: '**', redirectTo: '' }
];