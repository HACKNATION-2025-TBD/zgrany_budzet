import { Link } from "react-router";
import MC from "@/assets/mc.png";
import { Button } from "@/components/ui/button";
import LoginImage from "@/assets/login.png";
import { Home } from "lucide-react";
import { RoleCard } from "@/components/role-card";

export function meta() {
  return [{ title: "Login" }];
}

export default function Login() {
  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <header className="p-4 border-b border-gov-gray-500">
          <img src={MC} alt="Ministerstwo Cyfryzacji" width={150} />
        </header>
        <h1 className="font-semibold text-2xl py-6">Zaloguj się do usługi</h1>
        <p className="text-gov-gray-500">Wybierz rolę:</p>
        <nav className="flex flex-col gap-4 py-4 mr-8">
          <RoleCard 
            to="/dashboard"
            icon={Home}
            title="Kierownictwo"
            description="Komórka organizacyjna MC odpowiedzialna za planowanie budżetu"
          />
          <RoleCard 
            to="/dashboard"
            icon={Home}
            title="Biuro Budżetowo Finansowe"
            description="Kierownictwo Ministerstwa Cyfryzacji"
          />
          <RoleCard 
            to="/dashboard"
            icon={Home}
            title="Komórki organizacyjne"
            description="Departamenty i biura"
          />
        </nav>
      </div>
      <img src={LoginImage} alt="login image" className="rounded-lg h-[80vh] object-cover object-center" />
    </div>
  );
}
