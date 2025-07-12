from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db import IntegrityError, transaction


class JsonResponseHelper:

    @staticmethod
    def sucesso(dados_extras=None):

        resposta = {"success": True}
        if dados_extras:
            resposta.update(dados_extras)
        return JsonResponse(resposta)

    @staticmethod
    def erro(mensagem_erro, codigo_status=400, dados_extras=None):

        resposta = {"success": False, "error": mensagem_erro}
        if dados_extras:
            resposta.update(dados_extras)
        return JsonResponse(resposta, status=codigo_status)

    @staticmethod
    def erro_validacao_formulario(form):

        return JsonResponse({"success": False, "errors": form.errors}, status=400)


class UserObjectMixin:

    @staticmethod
    def buscar_objeto_do_usuario(model_class, usuario, pk, campo_usuario="user"):

        filtros = {"pk": pk, campo_usuario: usuario}
        return get_object_or_404(model_class, **filtros)


class NumericValidatorMixin:

    @staticmethod
    def validar_range_numerico(valor, valor_min, valor_max, nome_campo):

        if valor is not None and not (valor_min <= valor <= valor_max):
            raise ValidationError(
                f"{nome_campo} deve estar entre {valor_min} e {valor_max}."
            )
        return valor

    @staticmethod
    def validar_peso(peso):

        return NumericValidatorMixin.validar_range_numerico(peso, 0, 1000, "Peso")

    @staticmethod
    def validar_repeticoes(reps):

        return NumericValidatorMixin.validar_range_numerico(
            reps, 1, 1000, "Número de repetições"
        )

    @staticmethod
    def validar_series(sets):

        return NumericValidatorMixin.validar_range_numerico(
            sets, 1, 20, "Número de séries"
        )


class AjaxFormProcessorMixin:

    @staticmethod
    def processar_formulario_ajax(form, usuario=None, campo_usuario="user"):

        if form.is_valid():
            if usuario and hasattr(form, "instance"):
                setattr(form.instance, campo_usuario, usuario)
            form.save()
            return JsonResponseHelper.sucesso()
        else:
            return JsonResponseHelper.erro_validacao_formulario(form)

    @staticmethod
    def processar_edicao_ajax(model_class, pk, usuario, dados_post, campos_permitidos):

        try:
            objeto = UserObjectMixin.buscar_objeto_do_usuario(model_class, usuario, pk)

            campos_faltando = [
                campo for campo in campos_permitidos if not dados_post.get(campo)
            ]

            if campos_faltando:
                return JsonResponseHelper.erro(
                    f"Campos obrigatórios não fornecidos: {', '.join(campos_faltando)}"
                )

            for campo in campos_permitidos:
                valor = dados_post.get(campo)
                if valor is not None:

                    if hasattr(objeto._meta.get_field(campo), "decimal_places"):
                        valor = float(valor)
                    setattr(objeto, campo, valor)

            objeto.save()
            return JsonResponseHelper.sucesso()

        except ValueError:
            return JsonResponseHelper.erro("Dados inválidos fornecidos")
        except Exception as e:
            return JsonResponseHelper.erro(f"Erro ao salvar: {str(e)}")


class BaseUserFilterMixin:

    def get_queryset(self):

        return self.model.objects.filter(user=self.request.user)


class BaseUserCRUDMixin:

    def get_mensagem_sucesso_criacao(self):

        return f"{self.model._meta.verbose_name.title()} criado com sucesso!"

    def get_mensagem_sucesso_atualizacao(self):

        return f"{self.model._meta.verbose_name.title()} atualizado com sucesso!"

    def get_mensagem_erro_integridade(self):

        return f"Erro de integridade ao salvar {self.model._meta.verbose_name}."

    def tratar_erro_integridade(self, form, mensagem_erro=None):

        if not mensagem_erro:
            mensagem_erro = self.get_mensagem_erro_integridade()
        messages.error(self.request, mensagem_erro)
        return self.form_invalid(form)

    def tratar_sucesso(self, form, mensagem_sucesso=None):

        if not mensagem_sucesso:
            if (
                hasattr(self, "object")
                and self.object
                and getattr(self.object, "pk", None)
            ):
                mensagem_sucesso = self.get_mensagem_sucesso_atualizacao()
            else:
                mensagem_sucesso = self.get_mensagem_sucesso_criacao()
        messages.success(self.request, mensagem_sucesso)
        return super().form_valid(form)


class BaseUserCreateView(
    BaseUserCRUDMixin, LoginRequiredMixin, BaseUserFilterMixin, CreateView
):

    def form_valid(self, form):

        try:
            form.instance.user = self.request.user
            return self.tratar_sucesso(form)
        except IntegrityError:
            return self.tratar_erro_integridade(form)


class BaseUserUpdateView(
    BaseUserCRUDMixin, LoginRequiredMixin, BaseUserFilterMixin, UpdateView
):

    def form_valid(self, form):

        try:
            return self.tratar_sucesso(form)
        except IntegrityError:
            return self.tratar_erro_integridade(form)


class BaseUserDeleteView(LoginRequiredMixin, BaseUserFilterMixin, DeleteView):

    def get_mensagem_sucesso_exclusao(self):

        return f"{self.model._meta.verbose_name.title()} excluído com sucesso!"

    def delete(self, request, *args, **kwargs):

        self.object = self.get_object()
        mensagem = self.get_mensagem_sucesso_exclusao()
        messages.success(request, mensagem)
        return super().delete(request, *args, **kwargs)


class UniqueNameValidatorMixin:

    def validar_nome_unico(self, nome, campo_usuario="user", tamanho_minimo=2):

        if not nome:
            return nome

        nome = nome.strip()

        if len(nome) < tamanho_minimo:
            raise ValidationError(
                f"Nome deve ter pelo menos {tamanho_minimo} caracteres."
            )

        if hasattr(self, "user") and self.user:
            filtros = {"name__iexact": nome, campo_usuario: self.user}

            queryset = self._meta.model.objects.filter(**filtros)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                tipo_objeto = self._meta.model._meta.verbose_name
                raise ValidationError(f"Você já tem um {tipo_objeto} com este nome.")

        return nome


class AjaxCRUDMixin:

    def validar_permissao_usuario(self, objeto):

        if hasattr(objeto, "user") and objeto.user != self.request.user:
            return JsonResponseHelper.erro(
                "Você não tem permissão para modificar este item.", codigo_status=403
            )
        return None

    def processar_delete_ajax(self, model_class, pk, validar_dependencias=None):

        try:
            objeto = UserObjectMixin.buscar_objeto_do_usuario(
                model_class, self.request.user, pk
            )

            if validar_dependencias:
                erro_dependencia = validar_dependencias(objeto)
                if erro_dependencia:
                    return JsonResponseHelper.erro(erro_dependencia)

            nome_objeto = str(objeto)
            objeto.delete()

            return JsonResponseHelper.sucesso(
                {"message": f'"{nome_objeto}" excluído com sucesso!'}
            )

        except Exception as e:
            return JsonResponseHelper.erro(f"Erro ao excluir: {str(e)}")

    def processar_update_ajax(self, model_class, pk, form_class, **form_kwargs):

        try:
            objeto = UserObjectMixin.buscar_objeto_do_usuario(
                model_class, self.request.user, pk
            )

            form = form_class(self.request.POST, instance=objeto, **form_kwargs)

            if form.is_valid():
                form.save()
                return JsonResponseHelper.sucesso(
                    {"message": f'"{objeto}" atualizado com sucesso!'}
                )
            else:
                return JsonResponseHelper.erro_validacao_formulario(form)

        except IntegrityError:
            return JsonResponseHelper.erro("Erro de integridade ao atualizar.")
        except Exception as e:
            return JsonResponseHelper.erro(f"Erro ao atualizar: {str(e)}")


class ReorderMixin:

    def processar_reordenacao(
        self,
        model_class,
        lista_ids,
        campo_filtro=None,
        filtros_extras=None,
        campo_order="order",
        campo_id="pk",
    ):

        try:
            if not lista_ids:
                return JsonResponseHelper.erro("Lista de IDs não fornecida")

            filtros = {}
            if campo_filtro:
                filtros[campo_filtro] = self.request.user
            if filtros_extras:
                filtros.update(filtros_extras)

            with transaction.atomic():
                for i, item_id in enumerate(lista_ids, 1):
                    filtros_update = filtros.copy()
                    filtros_update[campo_id] = item_id

                    updated = model_class.objects.filter(**filtros_update).update(
                        **{campo_order: i}
                    )

                    if updated == 0:
                        return JsonResponseHelper.erro(
                            f"Item com ID {item_id} não encontrado ou sem permissão"
                        )

            return JsonResponseHelper.sucesso()

        except Exception as e:
            return JsonResponseHelper.erro(f"Erro ao reordenar: {str(e)}")


class ContextDataMixin:

    def calcular_metricas_basicas(self, queryset, campos_numericos=None):

        metricas = {
            "total_registros": queryset.count(),
            "primeiro_registro": queryset.first(),
            "ultimo_registro": queryset.last(),
        }

        if campos_numericos and queryset.exists():
            from django.db.models import Avg, Max, Min, Sum

            for campo in campos_numericos:
                agregacoes = queryset.aggregate(
                    **{
                        f"{campo}_avg": Avg(campo),
                        f"{campo}_max": Max(campo),
                        f"{campo}_min": Min(campo),
                        f"{campo}_sum": Sum(campo),
                    }
                )
                metricas.update(agregacoes)

        return metricas

    def preparar_dados_grafico(
        self, queryset, campo_data, campo_valor, formato_data="%d/%m", limite_dias=30
    ):

        from datetime import date, timedelta

        if limite_dias:
            data_limite = date.today() - timedelta(days=limite_dias)
            queryset = queryset.filter(**{f"{campo_data}__gte": data_limite})

        queryset = queryset.order_by(campo_data)

        if not queryset.exists():
            return {"labels": [], "data": [], "dates": [], "count": 0}

        registros = list(queryset)

        return {
            "labels": [
                getattr(registro, campo_data).strftime(formato_data)
                for registro in registros
            ],
            "data": [float(getattr(registro, campo_valor)) for registro in registros],
            "dates": [
                getattr(registro, campo_data).strftime("%Y-%m-%d")
                for registro in registros
            ],
            "count": len(registros),
        }
