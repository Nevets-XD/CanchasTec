import { Routes } from '@angular/router';
import { Home } from './home/home';
import { Creators } from './creators/creators';
import { LoginComponent } from './login/login';
import { RegisterComponent } from './register/register';

export const routes: Routes = [
  { path: '', component: Home }, // ruta principal
  { path: 'creators', component: Creators },
  { path: 'Login', component: LoginComponent },
  { path: 'Register', component: RegisterComponent }
];
